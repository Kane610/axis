# ruff: noqa: D100,D103

from __future__ import annotations

import asyncio
import getpass
import os
from pathlib import Path
from pprint import pformat
import re
from typing import TYPE_CHECKING, Any

from aiohttp import ClientSession
import tomli
import tomli_w
from zeroconf import IPVersion, ServiceStateChange
from zeroconf.asyncio import AsyncServiceBrowser, AsyncServiceInfo, AsyncZeroconf

from axis.device import AxisDevice
from axis.errors import Forbidden, PathNotFound, RequestError, Unauthorized
from axis.models.configuration import Configuration

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

DeviceEntry = dict[str, Any]
DeviceStore = dict[str, DeviceEntry]
DiscoveredDevice = dict[str, str]

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


def register(registry: object, router: object) -> None:
    """Register device-pack commands and menu nodes (explicit composition placeholder)."""


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
        print(  # noqa: T201
            f"  {idx}. {entry.get('name', '<unknown>')} "
            f"({entry.get('host', '<unknown>')}, mac={entry.get('macaddress', '')})"
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


def register_or_update_device(devices: DeviceStore) -> None:
    device_info = prompt_for_device()
    existing_serial_for_host = find_serial_by_host(devices, device_info["host"])
    if existing_serial_for_host is not None:
        update_existing = (
            input(
                f"A device with host {device_info['host']} already exists "
                f"(serial {existing_serial_for_host}). Update it? (y/n): "
            )
            .strip()
            .lower()
        )
        if update_existing != "y":
            print("Device registration aborted.")  # noqa: T201
            return

    config, serial, model, extra = asyncio.run(validate_and_fetch_device(device_info))
    if config is None or serial is None or model is None or extra is None:
        return

    migrate_unknown_entry(devices, serial, device_info["host"])

    if serial in devices:
        update = (
            input(
                f"A device with serial {serial} already exists. "
                "Update its configuration? (y/n): "
            )
            .strip()
            .lower()
        )
        if update != "y":
            print("Device registration aborted.")  # noqa: T201
            return

    devices[serial] = {
        "config": config_to_toml_dict(config),
        "model": model,
        "extra": extra,
    }
    print(f"Device '{serial}' registered/updated.")  # noqa: T201
