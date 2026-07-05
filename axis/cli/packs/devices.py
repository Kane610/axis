# ruff: noqa: D100,D103

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import getpass
import os
from pathlib import Path
from pprint import pformat
import re
import time
from typing import TYPE_CHECKING, Any

from aiohttp import ClientSession
import tomli
import tomli_w
from zeroconf import IPVersion, ServiceStateChange
from zeroconf.asyncio import AsyncServiceBrowser, AsyncServiceInfo, AsyncZeroconf

from axis.cli.core.contracts import CommandCapabilities, CommandResult
from axis.cli.core.router import MenuItem, MenuNode
from axis.device import AxisDevice
from axis.errors import Forbidden, PathNotFound, RequestError, Unauthorized
from axis.models.configuration import Configuration

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from axis.cli.core.context import CliContext
    from axis.cli.core.io import CliIO
    from axis.cli.core.registry import CommandRegistry
    from axis.cli.core.router import CliRouter


class _AddDeviceCommand:
    id = "devices.add"
    title = "Add additional device"
    capabilities = CommandCapabilities()

    async def run(self, ctx: CliContext, io: CliIO) -> CommandResult:
        devices = load_devices(ctx.config_path)
        result = await register_or_update_device_async(devices, io)
        if result.status != "ok":
            return result

        save_devices(ctx.config_path, devices)
        return result


class _DiscoverDevicesCommand:
    id = "devices.discover"
    title = "Discover devices"
    capabilities = CommandCapabilities()

    async def run(self, ctx: CliContext, io: CliIO) -> CommandResult:
        devices = load_devices(ctx.config_path)

        discovered_devices = await discover_axis_devices(scan_seconds=5.0)
        filtered_discovered = filter_discovered_devices(discovered_devices, devices)
        selected_discovered = select_discovered_device(filtered_discovered)
        if selected_discovered is None:
            return CommandResult(
                status="cancelled", message="Device discovery aborted."
            )

        username = io.prompt("Enter username: ").strip()
        password = io.prompt_password("Enter password: ")
        device_info = {
            "host": selected_discovered.get("host", "").strip(),
            "username": username,
            "password": password,
        }

        result = await register_or_update_device_async(
            devices,
            io,
            device_info=device_info,
        )
        if result.status == "ok":
            save_devices(ctx.config_path, devices)
        return result


class _SelectDeviceForOperationsCommand:
    id = "devices.operations"
    title = "Device operations"
    capabilities = CommandCapabilities()

    async def run(self, ctx: CliContext, io: CliIO) -> CommandResult:
        _ = io
        devices = load_devices(ctx.config_path)
        if not devices:
            return CommandResult(
                status="cancelled",
                message="No devices available.",
            )

        selected = select_device(devices)
        if selected is None:
            return CommandResult(status="cancelled", message="No device selected.")

        serial, device_entry = selected
        ctx.selected_serial = serial
        ctx.selected_device = device_entry
        return CommandResult(
            message=f"Selected device: {serial}",
            payload={"next_node_id": "device_operations"},
        )


def _render_devices_node(ctx: CliContext, io: CliIO) -> None:
    devices = load_devices(ctx.config_path)
    if not devices:
        io.write("\nNo devices registered yet.")
        return

    io.write("\nRegistered devices:")
    for idx, (serial, device_data) in enumerate(devices.items(), 1):
        host = str(device_data.get("config", {}).get("host", "<unknown>"))
        model = str(device_data.get("model", ""))
        io.write(f"  {idx}. {_format_device_label(model, serial, host)}")


DeviceEntry = dict[str, Any]
DeviceStore = dict[str, DeviceEntry]
DiscoveredDevice = dict[str, str]


@dataclass
class HealthCheckResult:
    """Result of device health check operation."""

    success: bool
    response_time_ms: float | None = None
    model: str | None = None
    firmware: str | None = None
    error: str | None = None


AXIS_SERVICE_TYPE = "_axis-video._tcp.local."
AXIS_OUI = {"00:40:8c", "ac:cc:8e", "b8:a4:4f", "e8:27:25"}

_HEX_ONLY_RE = re.compile(r"[^0-9a-f]")
_AXIS_OUI_NORMALIZED = {prefix.replace(":", "") for prefix in AXIS_OUI}


def _debug_enabled() -> bool:
    value = os.getenv("AXIS_CLI_DEBUG", "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def _debug_dump(label: str, payload: object) -> None:
    if _debug_enabled():
        print(f"[debug] {label}:\n{pformat(payload)}")  # noqa: T201


def register(registry: CommandRegistry, router: CliRouter) -> None:
    """Register device-pack commands and menu nodes."""
    registry.register_command(_AddDeviceCommand())
    registry.register_command(_DiscoverDevicesCommand())
    registry.register_command(_SelectDeviceForOperationsCommand())

    router.register_node(
        MenuNode(
            id="devices",
            title="Devices",
            parent_id="main",
            render=_render_devices_node,
            items=[
                MenuItem(
                    key="1",
                    label="Add additional device",
                    action="command",
                    command_id="devices.add",
                ),
                MenuItem(
                    key="2",
                    label="Discover devices",
                    action="command",
                    command_id="devices.discover",
                ),
                MenuItem(
                    key="3",
                    label="Device operations",
                    action="command",
                    command_id="devices.operations",
                ),
            ],
        )
    )


def get_config_path() -> Path:
    config_dir = Path.home() / ".axis"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.toml"


def load_devices(config_path: Path) -> DeviceStore:
    if not config_path.exists():
        return {}

    with config_path.open("rb") as file_handle:
        data = tomli.load(file_handle)

    devices = data.get("devices", {})
    if not isinstance(devices, dict):
        return {}
    return devices


def to_toml_compatible(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)):
        return value

    if value is None:
        return ""

    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, nested_value in value.items():
            normalized[str(key)] = to_toml_compatible(nested_value)
        return normalized

    if isinstance(value, (list, tuple)):
        return [to_toml_compatible(item) for item in value]

    return str(value)


def save_devices(config_path: Path, devices: DeviceStore) -> None:
    with config_path.open("wb") as file_handle:
        tomli_w.dump({"devices": to_toml_compatible(devices)}, file_handle)


async def fetch_device_serial_and_extra(
    config: Configuration,
) -> tuple[str, str, dict[str, Any]]:
    device = AxisDevice(config)
    try:
        basic_info = await device.vapix.basic_device_info.get_all_properties()
        _debug_dump("basic-device-info raw", basic_info)
        serial = extract_serial_number(basic_info)
        model = extract_model_number(basic_info)
        return serial, model, basic_info
    except (Forbidden, PathNotFound, RequestError, Unauthorized) as exc:
        _debug_dump(
            "basic-device-info failed, trying param.cgi fallback",
            {
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        )

    property_loaded = await device.vapix.params.property_handler.update()
    brand_loaded = await device.vapix.params.brand_handler.update()

    if property_loaded:
        serial = str(device.vapix.serial_number or "unknown")
        model = str(device.vapix.product_number or "") if brand_loaded else ""
        fallback_info: dict[str, Any] = {
            "serial_number": serial,
            "product_number": model,
            "source": "param.cgi",
        }
        _debug_dump("param.cgi fallback raw", fallback_info)
        return serial, model, fallback_info

    msg = "Unable to fetch device info from basic-device-info or param.cgi"
    raise RequestError(msg)


def extract_model_number(info: dict[str, Any]) -> str:
    for key in ("product_number", "ProdNbr"):
        value = info.get(key)
        if value:
            return str(value)

    item = info.get("0")
    if item is None:
        return ""

    model = getattr(item, "product_number", None)
    if model:
        return str(model)

    if isinstance(item, dict):
        for key in ("product_number", "ProdNbr"):
            value = item.get(key)
            if value:
                return str(value)

    return ""


def extract_serial_number(info: dict[str, Any]) -> str:
    for key in ("serial_number", "serialNumber", "SerialNumber"):
        value = info.get(key)
        if value:
            return str(value)

    item = info.get("0")
    if item is None:
        return "unknown"

    item_serial = getattr(item, "serial_number", None)
    if item_serial:
        return str(item_serial)

    if isinstance(item, dict):
        for key in ("serial_number", "serialNumber", "SerialNumber"):
            value = item.get(key)
            if value:
                return str(value)

    return "unknown"


def prompt_for_device() -> dict[str, str]:
    host = input("Enter device host/IP: ").strip()
    username = input("Enter username: ").strip()
    password = getpass.getpass("Enter password: ")
    return {"host": host, "username": username, "password": password}


def config_to_toml_dict(config: Configuration) -> dict[str, Any]:
    return {
        "host": config.host,
        "username": config.username,
        "password": config.password,
        "port": config.port,
        "web_proto": str(config.web_proto),
        "verify_ssl": config.verify_ssl,
        "is_companion": config.is_companion,
        "auth_scheme": str(config.auth_scheme),
        "websocket_enabled": config.websocket_enabled,
        "websocket_force": config.websocket_force,
    }


def _normalize_macaddress(value: str) -> str:
    lowered = value.strip().lower().rstrip("*")
    return _HEX_ONLY_RE.sub("", lowered)


def is_axis_macaddress(macaddress: str) -> bool:
    normalized = _normalize_macaddress(macaddress)
    if len(normalized) < 6:
        return False
    return normalized[:6] in _AXIS_OUI_NORMALIZED


def _extract_macaddress_property(properties: dict[bytes, bytes | None]) -> str | None:
    for raw_key, raw_value in properties.items():
        key = raw_key.decode("utf-8", errors="ignore").strip().lower()
        if key != "macaddress":
            continue
        if raw_value is None:
            continue
        value = raw_value.decode("utf-8", errors="ignore").strip()
        if value:
            return value
    return None


def _decode_discovery_properties(
    properties: dict[bytes, bytes | None],
) -> dict[str, str]:
    """Decode Zeroconf TXT properties to normalized string key/value pairs."""
    decoded: dict[str, str] = {}
    for raw_key, raw_value in properties.items():
        key = raw_key.decode("utf-8", errors="ignore").strip().lower()
        if not key or raw_value is None:
            continue
        value = raw_value.decode("utf-8", errors="ignore").strip()
        if value:
            decoded[key] = value
    return decoded


def _extract_discovery_metadata(
    properties: dict[bytes, bytes | None],
) -> dict[str, str]:
    """Extract user-facing metadata fields from Zeroconf TXT properties."""
    decoded = _decode_discovery_properties(properties)
    fields: dict[str, tuple[str, ...]] = {
        "module": ("module", "hw", "hardware", "hardwareid"),
        "model": ("model", "modelname", "prodshortname", "prodfullname"),
        "serial": ("serial", "serialnumber"),
        "firmware": ("firmware", "version", "firmwareversion"),
        "vendor": ("vendor", "manufacturer", "brand"),
    }

    metadata: dict[str, str] = {}
    for label, aliases in fields.items():
        for alias in aliases:
            value = decoded.get(alias)
            if value:
                metadata[label] = value
                break

    return metadata


def _zeroconf_instance_name(service_name: str) -> str:
    suffix = f".{AXIS_SERVICE_TYPE}"
    if service_name.endswith(suffix):
        return service_name[: -len(suffix)]
    return service_name


def _normalize_device_identifier(value: str) -> str:
    return _HEX_ONLY_RE.sub("", value.strip().lower())


def filter_discovered_devices(
    discovered_devices: list[DiscoveredDevice],
    registered_devices: DeviceStore,
) -> list[DiscoveredDevice]:
    """Filter out discovered devices that are already registered."""
    registered_hosts = {
        str(entry.get("config", {}).get("host", "")).strip().lower()
        for entry in registered_devices.values()
    }

    registered_serial_ids = {
        _normalize_device_identifier(serial)
        for serial in registered_devices
        if _normalize_device_identifier(serial)
    }

    filtered: list[DiscoveredDevice] = []
    for discovered in discovered_devices:
        host = discovered.get("host", "").strip().lower()
        if host and host in registered_hosts:
            continue

        macaddress = discovered.get("macaddress", "")
        normalized_mac = _normalize_device_identifier(macaddress)
        if normalized_mac and normalized_mac in registered_serial_ids:
            continue

        filtered.append(discovered)

    return filtered


async def discover_axis_devices(scan_seconds: float = 5.0) -> list[DiscoveredDevice]:
    """Discover Axis devices advertised via Zeroconf axis-video service."""
    discovered_names: set[str] = set()

    def _on_service_state_change(
        zeroconf: object,
        service_type: str,
        name: str,
        state_change: object,
    ) -> None:
        _ = (zeroconf, service_type)
        if state_change in {ServiceStateChange.Added, ServiceStateChange.Updated}:
            discovered_names.add(name)

    azc = AsyncZeroconf(ip_version=IPVersion.V4Only)
    browser = AsyncServiceBrowser(
        azc.zeroconf,
        [AXIS_SERVICE_TYPE],
        handlers=[_on_service_state_change],
    )
    try:
        await asyncio.sleep(scan_seconds)

        entries: list[DiscoveredDevice] = []
        seen_hosts: set[str] = set()
        for service_name in sorted(discovered_names):
            info = AsyncServiceInfo(AXIS_SERVICE_TYPE, service_name)
            if not await info.async_request(azc.zeroconf, timeout=1500):
                continue

            macaddress = _extract_macaddress_property(info.properties)
            if not macaddress or not is_axis_macaddress(macaddress):
                continue

            addresses = info.parsed_addresses(IPVersion.V4Only)
            if not addresses:
                continue

            host = addresses[0]
            if host in seen_hosts:
                continue
            seen_hosts.add(host)

            entries.append(
                {
                    "host": host,
                    "name": _zeroconf_instance_name(service_name),
                    "macaddress": macaddress,
                    **_extract_discovery_metadata(info.properties),
                }
            )

        return entries
    finally:
        await browser.async_cancel()
        await azc.async_close()


def select_discovered_device(
    discovered_devices: list[DiscoveredDevice],
) -> DiscoveredDevice | None:
    """Select a discovered device from a numbered list."""
    if not discovered_devices:
        print("\nNo discoverable Axis devices were found.")  # noqa: T201
        return None

    print("\nDiscovered Axis devices:")  # noqa: T201
    for idx, entry in enumerate(discovered_devices, 1):
        metadata_parts = [
            f"module={entry['module']}" if entry.get("module") else "",
            f"model={entry['model']}" if entry.get("model") else "",
            f"serial={entry['serial']}" if entry.get("serial") else "",
            f"firmware={entry['firmware']}" if entry.get("firmware") else "",
        ]
        metadata = ", ".join(part for part in metadata_parts if part)
        metadata_suffix = f", {metadata}" if metadata else ""
        print(  # noqa: T201
            f"  {idx}. {entry.get('name', '<unknown>')} "
            f"({entry.get('host', '<unknown>')}, mac={entry.get('macaddress', '')}"
            f"{metadata_suffix})"
        )
    print("  b. Back")  # noqa: T201
    print("  e. Exit")  # noqa: T201

    selection = input("Select discovered device [b/e]: ").strip().lower()
    if selection == "e":
        print("Exiting.")  # noqa: T201
        raise SystemExit(0)
    if selection == "b":
        return None

    try:
        index = int(selection)
    except ValueError:
        print("Invalid selection.")  # noqa: T201
        return None

    if index < 1 or index > len(discovered_devices):
        print("Invalid selection.")  # noqa: T201
        return None

    return discovered_devices[index - 1]


def _format_device_label(model: str, serial: str, host: str) -> str:
    if model:
        return f"{model} {serial} ({host})"
    return f"{serial} ({host})"


def _format_device_operations_label(serial: str, device_entry: DeviceEntry) -> str:
    config_data = device_entry.get("config", {})
    host = str(config_data.get("host", "<unknown>"))
    model = str(device_entry.get("model", "")).strip()
    friendly_name = model if model else serial
    return f"{friendly_name} ({host}, mac={serial})"


async def validate_and_fetch_device(
    device_info: dict[str, str],
) -> tuple[Configuration | None, str | None, str | None, dict[str, Any] | None]:
    async def _attempt(
        session: ClientSession,
        is_companion: bool,
    ) -> tuple[Configuration, str, str, dict[str, Any]]:
        config = Configuration(
            session=session,
            host=device_info["host"],
            username=device_info["username"],
            password=device_info["password"],
            is_companion=is_companion,
        )
        serial, model, extra = await fetch_device_serial_and_extra(config)
        return config, serial, model, extra

    try:
        async with ClientSession() as session:
            try:
                _debug_dump(
                    "device validation attempt",
                    {
                        "host": device_info.get("host", ""),
                        "is_companion": False,
                    },
                )
                return await _attempt(session, is_companion=False)
            except (RequestError, OSError) as exc:
                _debug_dump(
                    "device validation failure",
                    {
                        "host": device_info.get("host", ""),
                        "is_companion": False,
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                    },
                )
                print("Retrying with companion mode enabled...")  # noqa: T201
                _debug_dump(
                    "device validation attempt",
                    {
                        "host": device_info.get("host", ""),
                        "is_companion": True,
                    },
                )
                return await _attempt(session, is_companion=True)
    except RequestError as exc:
        _debug_dump(
            "device validation failure",
            {
                "host": device_info.get("host", ""),
                "is_companion": True,
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        )
        print(f"Failed to connect to device: {exc}")  # noqa: T201
        print("Please verify host reachability and credentials, then try again.")  # noqa: T201
        return None, None, None, None
    except (ValueError, KeyError, OSError) as exc:
        _debug_dump(
            "device validation failure",
            {
                "host": device_info.get("host", ""),
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        )
        print(f"Failed to fetch device info: {exc}")  # noqa: T201
        print("Please check your credentials and try again.")  # noqa: T201
        return None, None, None, None


def print_registered_devices(devices: DeviceStore) -> None:
    if not devices:
        print("\nNo devices registered yet.")  # noqa: T201
        return

    print("\nRegistered devices:")  # noqa: T201
    for idx, (serial, device_data) in enumerate(devices.items(), 1):
        host = str(device_data.get("config", {}).get("host", "<unknown>"))
        model = str(device_data.get("model", ""))
        print(f"  {idx}. {_format_device_label(model, serial, host)}")  # noqa: T201


def migrate_unknown_entry(devices: DeviceStore, serial: str, host: str) -> None:
    if serial == "unknown" or "unknown" not in devices:
        return

    unknown_host = str(devices.get("unknown", {}).get("config", {}).get("host", ""))
    if unknown_host == host:
        devices.pop("unknown", None)


def find_serial_by_host(devices: DeviceStore, host: str) -> str | None:
    for serial, device_data in devices.items():
        existing_host = str(device_data.get("config", {}).get("host", ""))
        if existing_host == host:
            return serial
    return None


def select_device(devices: DeviceStore) -> tuple[str, DeviceEntry] | None:
    if not devices:
        print("\nNo devices available.")  # noqa: T201
        return None

    entries = list(devices.items())
    print("\nSelect a device:")  # noqa: T201
    for idx, (serial, device_data) in enumerate(entries, 1):
        host = str(device_data.get("config", {}).get("host", "<unknown>"))
        model = str(device_data.get("model", ""))
        print(f"  {idx}. {_format_device_label(model, serial, host)}")  # noqa: T201
    print("  b. Back")  # noqa: T201
    print("  e. Exit")  # noqa: T201

    selection = input("Select device [b/e]: ").strip().lower()
    if selection == "e":
        print("Exiting.")  # noqa: T201
        raise SystemExit(0)
    if selection == "b":
        return None

    try:
        index = int(selection)
    except ValueError:
        print("Invalid selection.")  # noqa: T201
        return None

    if index < 1 or index > len(entries):
        print("Invalid selection.")  # noqa: T201
        return None

    return entries[index - 1]


def get_device_credentials(device_entry: DeviceEntry) -> dict[str, str] | None:
    config_data = device_entry.get("config", {})
    if not isinstance(config_data, dict):
        return None

    host = str(config_data.get("host", "")).strip()
    username = str(config_data.get("username", "")).strip()
    password = str(config_data.get("password", ""))
    if not host or not username:
        return None

    return {
        "host": host,
        "username": username,
        "password": password,
    }


async def run_on_selected_device[ReturnT](
    device_entry: DeviceEntry,
    operation: Callable[[AxisDevice], Awaitable[ReturnT]],
) -> ReturnT | None:
    credentials = get_device_credentials(device_entry)
    if credentials is None:
        print("Stored device config is incomplete. Please re-add the device.")  # noqa: T201
        return None

    try:
        async with ClientSession() as session:
            config = Configuration(
                session=session,
                host=credentials["host"],
                username=credentials["username"],
                password=credentials["password"],
            )
            device = AxisDevice(config)
            return await operation(device)
    except RequestError as exc:
        print(f"Device request failed: {exc}")  # noqa: T201
    except (ValueError, KeyError, OSError) as exc:
        print(f"Failed to connect to selected device: {exc}")  # noqa: T201
    return None


async def register_or_update_device_async(
    devices: DeviceStore,
    io: CliIO,
    *,
    device_info: dict[str, str] | None = None,
) -> CommandResult:
    """Register or update a device in-place.

    Returns:
        CommandResult describing update status and user-facing message.

    """
    if device_info is None:
        device_info = {
            "host": io.prompt("Enter device host/IP: ").strip(),
            "username": io.prompt("Enter username: ").strip(),
            "password": io.prompt_password("Enter password: "),
        }
    existing_serial_for_host = find_serial_by_host(devices, device_info["host"])
    if existing_serial_for_host is not None:
        update_existing = (
            io.prompt(
                f"A device with host {device_info['host']} already exists "
                f"(serial {existing_serial_for_host}). Update it? (y/n): "
            )
            .strip()
            .lower()
        )
        if update_existing != "y":
            return CommandResult(
                status="cancelled",
                message="Device registration aborted.",
            )

    config, serial, model, extra = await validate_and_fetch_device(device_info)
    if config is None or serial is None or model is None or extra is None:
        return CommandResult(
            status="error",
            message="Unable to validate device.",
        )

    migrate_unknown_entry(devices, serial, device_info["host"])

    if serial in devices:
        update = (
            io.prompt(
                f"A device with serial {serial} already exists. "
                "Update its configuration? (y/n): "
            )
            .strip()
            .lower()
        )
        if update != "y":
            return CommandResult(
                status="cancelled",
                message="Device registration aborted.",
            )

    devices[serial] = {
        "config": config_to_toml_dict(config),
        "model": model,
        "extra": extra,
    }
    return CommandResult(message=f"Device '{serial}' registered/updated.")


def register_or_update_device(devices: DeviceStore) -> None:
    """Legacy sync wrapper for register/update flow."""
    io = _TerminalIOAdapter()
    result = asyncio.run(
        register_or_update_device_async(
            devices,
            io,
            device_info=prompt_for_device(),
        )
    )
    if result.message:
        io.write(result.message)
    if result.status != "ok":
        return


class _TerminalIOAdapter:
    """Minimal local adapter for legacy sync flow."""

    def prompt(self, text: str) -> str:
        return input(text)

    def prompt_password(self, text: str) -> str:
        return getpass.getpass(text)

    def write(self, text: str) -> None:
        print(text)  # noqa: T201


def delete_device(serial: str, devices: DeviceStore) -> bool:
    """Remove device from registry after confirmation.

    Args:
        serial: Device serial number
        devices: Device store dict

    Returns:
        True if deleted, False if user canceled or device not found

    """
    if serial not in devices:
        print(f"Device {serial} not found.")  # noqa: T201
        return False

    device_label = _format_device_operations_label(serial, devices[serial])
    confirm = input(
        f"⚠️  This will DELETE:\n  {device_label}\n\n"
        "Type 'delete' to confirm, or press Enter to cancel: "
    ).strip()

    if confirm == "delete":
        del devices[serial]
        print("✓ Device deleted.")  # noqa: T201
        return True

    print("Cancelled.")  # noqa: T201
    return False


async def edit_device_credentials(
    serial: str, device_entry: DeviceEntry
) -> DeviceEntry | None:
    """Update device credentials and validate connectivity.

    Prompts user for each field (or skip with Enter to keep current value).
    Validates new credentials by attempting connection.

    Args:
        serial: Device serial number
        device_entry: Current device entry

    Returns:
        Updated device_entry if validation succeeds, None if validation fails or user cancels

    """
    config_dict = device_entry.get("config", {})
    if not isinstance(config_dict, dict):
        print("Device config is invalid.")  # noqa: T201
        return None

    print(f"\nEdit credentials for device {serial}")  # noqa: T201
    print("(Press Enter to keep current value)\n")  # noqa: T201

    # Prompt for fields
    host = input(  # noqa: ASYNC250
        f"  Host [{config_dict.get('host', '')}]: "
    ).strip() or config_dict.get("host")
    username = input(  # noqa: ASYNC250
        f"  Username [{config_dict.get('username', '')}]: "
    ).strip() or config_dict.get("username")
    port_str = input(f"  Port [{config_dict.get('port', 80)}]: ").strip()  # noqa: ASYNC250
    port = int(port_str) if port_str else config_dict.get("port", 80)
    password_input = getpass.getpass("  Password (press Enter to keep current): ")
    password = password_input if password_input else config_dict.get("password")

    # Build new device info and validate
    new_device_info: dict[str, str] = {
        "host": str(host),
        "username": str(username),
        "password": str(password),
    }

    print("\nValidating new credentials...")  # noqa: T201
    config, _serial_verify, model, extra = await validate_and_fetch_device(
        new_device_info
    )

    if config is None:
        print("✗ Validation failed. Credentials not updated.")  # noqa: T201
        return None

    # Update port after validation
    config.port = port

    # Update and return
    updated_entry = {
        "config": config_to_toml_dict(config),
        "model": model or device_entry.get("model"),
        "extra": extra or device_entry.get("extra", {}),
    }
    print("✓ Credentials updated and validated.")  # noqa: T201
    return updated_entry


async def health_check_device(
    serial: str, device_entry: DeviceEntry
) -> HealthCheckResult:
    """Check device connectivity and retrieve basic info.

    Args:
        serial: Device serial number
        device_entry: Device entry with config

    Returns:
        HealthCheckResult with success flag, response time, model, firmware, and error

    """
    config_dict = device_entry.get("config", {})
    if not isinstance(config_dict, dict):
        return HealthCheckResult(
            success=False,
            error="Device config is invalid.",
        )

    device_info = {
        "host": str(config_dict.get("host", "")),
        "username": str(config_dict.get("username", "")),
        "password": str(config_dict.get("password", "")),
    }

    if not device_info["host"] or not device_info["username"]:
        return HealthCheckResult(
            success=False,
            error="Device config is incomplete.",
        )

    print(f"Checking device health for {serial}...")  # noqa: T201

    start = time.perf_counter()

    try:
        config, _serial_verify, model, extra = await validate_and_fetch_device(
            device_info
        )
        if config is None:
            return HealthCheckResult(
                success=False,
                error="Failed to connect to device.",
            )
        elapsed = (time.perf_counter() - start) * 1000  # ms

        firmware = ""
        if isinstance(extra, dict):
            firmware = str(extra.get("firmware", "")).strip()

        return HealthCheckResult(
            success=True,
            response_time_ms=elapsed,
            model=model,
            firmware=firmware if firmware else None,
        )
    except Exception as exc:  # noqa: BLE001
        return HealthCheckResult(
            success=False,
            error=str(exc),
        )
