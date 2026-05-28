"""Axis CLI for local device registry management.

This module implements a small interactive command-line workflow for adding and
updating Axis device connection entries in ``~/.axis/config.toml``.

Current responsibilities:
        - Read/write a local TOML-backed device registry.
        - Prompt for host/username/password.
        - Validate connectivity and authentication by creating a ``Configuration``
            and calling basic-device-info through ``AxisDevice``.
        - Extract a stable device serial from multiple payload shapes
            (including ``{"0": DeviceInformation(...)}``).
        - Keep device data split into:
                - ``config``: connection settings used by the library.
                - ``extra``: fetched metadata from the device API.
        - Safely serialize nested values to TOML-friendly primitives.
        - Gracefully handle common failures (request/connection/validation errors)
            without crashing the interactive loop.

Update behavior:
        - If the entered host already exists, prompt for confirmation before update.
        - If the resolved serial already exists, prompt for confirmation before update.
        - If a legacy ``unknown`` entry exists for the same host and a real serial is
            resolved, migrate that entry to the resolved serial key.

Extension points:
        - Add more menu options in ``main()``.
        - Add pre-save transformations in ``config_to_toml_dict()``.
        - Add richer metadata normalization in ``to_toml_compatible()``.
        - Add additional identity-matching logic in ``extract_serial_number()`` and
            ``find_serial_by_host()``.
"""

import asyncio
import getpass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from aiohttp import ClientSession
import tomli
import tomli_w

from axis.device import AxisDevice
from axis.errors import Forbidden, PathNotFound, RequestError
from axis.models.configuration import Configuration
from axis.models.pwdgrp_cgi import SecondaryGroup

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Mapping

DeviceEntry = dict[str, Any]
DeviceStore = dict[str, DeviceEntry]


def get_config_path() -> Path:
    """Get the path to the config file, creating directory if needed."""
    config_dir = Path.home() / ".axis"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.toml"


def load_devices(config_path: Path) -> DeviceStore:
    """Load devices from TOML config file."""
    if not config_path.exists():
        return {}

    with config_path.open("rb") as file_handle:
        data = tomli.load(file_handle)

    devices = data.get("devices", {})
    if not isinstance(devices, dict):
        return {}
    return devices


def save_devices(config_path: Path, devices: DeviceStore) -> None:
    """Save devices to TOML config file."""
    with config_path.open("wb") as file_handle:
        tomli_w.dump({"devices": to_toml_compatible(devices)}, file_handle)


def to_toml_compatible(value: Any) -> Any:
    """Convert nested values to TOML-compatible primitives."""
    if isinstance(value, (str, int, float, bool)):
        return value

    if value is None:
        # TOML has no null type; use an empty string for missing optional values.
        return ""

    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, nested_value in value.items():
            normalized[str(key)] = to_toml_compatible(nested_value)
        return normalized

    if isinstance(value, (list, tuple)):
        return [to_toml_compatible(item) for item in value]

    # Fallback for custom objects (e.g. dataclasses, enums, model objects).
    return str(value)


async def fetch_device_serial_and_extra(
    config: Configuration,
) -> tuple[str, str, dict[str, Any]]:
    """Fetch device serial, model number, and extra info from a device."""
    device = AxisDevice(config)
    info = await device.vapix.basic_device_info.get_all_properties()
    serial = extract_serial_number(info)
    model = extract_model_number(info)
    return serial, model, info


def extract_model_number(info: dict[str, Any]) -> str:
    """Extract the product/model number from a basic-device-info payload."""
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
    """Extract a stable serial from basic-device-info payload variants."""
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
    """Prompt user for device credentials interactively."""
    host = input("Enter device host/IP: ").strip()
    username = input("Enter username: ").strip()
    password = getpass.getpass("Enter password: ")
    return {"host": host, "username": username, "password": password}


def config_to_toml_dict(config: Configuration) -> dict[str, Any]:
    """Convert a Configuration object to a dict for TOML serialization."""
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


def _format_device_label(model: str, serial: str, host: str) -> str:
    """Format a device label as 'Model serial (IP)' or 'serial (IP)' if no model."""
    if model:
        return f"{model} {serial} ({host})"
    return f"{serial} ({host})"


async def validate_and_fetch_device(
    device_info: dict[str, str],
) -> tuple[Configuration | None, str | None, str | None, dict[str, Any] | None]:
    """Validate a device and fetch serial/model/extra info."""
    try:
        async with ClientSession() as session:
            config = Configuration(
                session=session,
                host=device_info["host"],
                username=device_info["username"],
                password=device_info["password"],
            )
            serial, model, extra = await fetch_device_serial_and_extra(config)
            return config, serial, model, extra
    except RequestError as exc:
        print(f"Failed to connect to device: {exc}")  # noqa: T201
        print("Please verify host reachability and credentials, then try again.")  # noqa: T201
        return None, None, None, None
    except (ValueError, KeyError, OSError) as exc:
        print(f"Failed to fetch device info: {exc}")  # noqa: T201
        print("Please check your credentials and try again.")  # noqa: T201
        return None, None, None, None


def print_registered_devices(devices: DeviceStore) -> None:
    """Print the currently registered devices."""
    if not devices:
        print("\nNo devices registered yet.")  # noqa: T201
        return

    print("\nRegistered devices:")  # noqa: T201
    for idx, (serial, device_data) in enumerate(devices.items(), 1):
        host = str(device_data.get("config", {}).get("host", "<unknown>"))
        model = str(device_data.get("model", ""))
        print(f"  {idx}. {_format_device_label(model, serial, host)}")  # noqa: T201


def migrate_unknown_entry(devices: DeviceStore, serial: str, host: str) -> None:
    """Move legacy unknown entry to resolved serial for the same host."""
    if serial == "unknown" or "unknown" not in devices:
        return

    unknown_host = str(devices.get("unknown", {}).get("config", {}).get("host", ""))
    if unknown_host == host:
        devices.pop("unknown", None)


def find_serial_by_host(devices: DeviceStore, host: str) -> str | None:
    """Find an existing device serial by host value."""
    for serial, device_data in devices.items():
        existing_host = str(device_data.get("config", {}).get("host", ""))
        if existing_host == host:
            return serial
    return None


def select_device(devices: DeviceStore) -> tuple[str, DeviceEntry] | None:
    """Prompt for device selection from the registry."""
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
    """Extract credentials for connecting to a stored device entry."""
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
    """Run an async operation against a selected device with shared error handling."""
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


async def fetch_supported_apis(device_entry: DeviceEntry) -> list[dict[str, str]]:
    """Retrieve supported APIs from API discovery for a selected device."""

    async def _operation(device: AxisDevice) -> list[dict[str, str]]:
        await device.vapix.api_discovery.update()
        return [
            {
                "id": api.id,
                "name": api.name,
                "version": api.version,
                "status": str(api.status),
            }
            for api in device.vapix.api_discovery.values()
        ]

    result = await run_on_selected_device(device_entry, _operation)
    if result is None:
        return []
    return result


def list_supported_apis_flow(serial: str, device_entry: DeviceEntry) -> None:
    """List supported APIs for a selected device."""
    apis = asyncio.run(fetch_supported_apis(device_entry))
    if not apis:
        print("No APIs discovered for this device.")  # noqa: T201
        return

    print(f"\nSupported APIs for {serial}:")  # noqa: T201
    for idx, api in enumerate(apis, 1):
        print(  # noqa: T201
            f"  {idx}. {api['id']} | {api['name']} | "
            f"v{api['version']} | {api['status']}"
        )


async def run_api_read_action(device_entry: DeviceEntry, api_id: str) -> None:
    """Run a safe read-only action for the selected API."""

    async def _operation(device: AxisDevice) -> None:
        if api_id == "basic-device-info":
            info = await device.vapix.basic_device_info.get_all_properties()
            item = info.get("0")
            if item is None:
                print("No basic device information found.")  # noqa: T201
                return
            serial_number = str(getattr(item, "serial_number", "unknown"))
            product_name = str(getattr(item, "product_full_name", "unknown"))
            firmware = str(getattr(item, "firmware_version", "unknown"))
            print("\nBasic device info:")  # noqa: T201
            print(f"  Serial: {serial_number}")  # noqa: T201
            print(f"  Product: {product_name}")  # noqa: T201
            print(f"  Firmware: {firmware}")  # noqa: T201
            return

        if api_id == "api-discovery":
            versions = await device.vapix.api_discovery.get_supported_versions()
            print("\nAPI Discovery supported versions:")  # noqa: T201
            for version in versions:
                print(f"  - {version}")  # noqa: T201
            return

        if api_id == "user-management":
            groups = await device.vapix.user_groups.get_user_groups()
            user = groups.get("0")
            if user is None:
                print("Current user group information is unavailable.")  # noqa: T201
                return
            print("\nCurrent user rights:")  # noqa: T201
            print(f"  Username: {user.name}")  # noqa: T201
            print(f"  Privileges: {user.privileges.value}")  # noqa: T201
            return

        print(f"No read action implemented yet for API '{api_id}'.")  # noqa: T201

    await run_on_selected_device(device_entry, _operation)


def api_drill_down_flow(device_entry: DeviceEntry) -> None:
    """Allow selecting an API and running API-specific actions."""
    apis = asyncio.run(fetch_supported_apis(device_entry))
    if not apis:
        print("No APIs discovered for this device.")  # noqa: T201
        return

    while True:
        print("\nAPI drill-down:")  # noqa: T201
        for idx, api in enumerate(apis, 1):
            print(  # noqa: T201
                f"  {idx}. {api['id']} | {api['name']} | "
                f"v{api['version']} | {api['status']}"
            )
        print("  b. Back")  # noqa: T201
        print("  e. Exit")  # noqa: T201

        selection = input("Select API [b/e]: ").strip().lower()
        if selection == "e":
            print("Exiting.")  # noqa: T201
            raise SystemExit(0)
        if selection == "b":
            return

        try:
            index = int(selection)
        except ValueError:
            print("Invalid selection.")  # noqa: T201
            continue

        if index < 1 or index > len(apis):
            print("Invalid selection.")  # noqa: T201
            continue

        selected_api = apis[index - 1]
        print("\nSelected API:")  # noqa: T201
        print(f"  ID: {selected_api['id']}")  # noqa: T201
        print(f"  Name: {selected_api['name']}")  # noqa: T201
        print(f"  Version: {selected_api['version']}")  # noqa: T201
        print(f"  Status: {selected_api['status']}")  # noqa: T201

        print("\nAPI actions:")  # noqa: T201
        print("  1. Run read action")  # noqa: T201
        print("  b. Back")  # noqa: T201
        print("  e. Exit")  # noqa: T201
        action_choice = input("Select action [1/b/e]: ").strip().lower()
        if action_choice == "e":
            print("Exiting.")  # noqa: T201
            raise SystemExit(0)
        if action_choice == "b":
            continue
        if action_choice != "1":
            print("Invalid option. Please enter 1, b, or e.")  # noqa: T201
            continue

        asyncio.run(run_api_read_action(device_entry, selected_api["id"]))


# ---------------------------------------------------------------------------
# Phase 3 - Event workflows
# ---------------------------------------------------------------------------


async def fetch_event_instances(
    device_entry: DeviceEntry,
) -> list[dict[str, str]]:
    """Retrieve event instances from a selected device."""

    async def _operation(device: AxisDevice) -> list[dict[str, str]]:
        await device.vapix.event_instances.update()
        return [
            {
                "topic": ev.topic,
                "name": ev.name,
                "stateful": str(ev.stateful),
                "stateless": str(ev.stateless),
                "available": str(ev.is_available),
            }
            for ev in device.vapix.event_instances.values()
        ]

    result = await run_on_selected_device(device_entry, _operation)
    return result if result is not None else []


def list_event_instances_flow(
    serial: str, device_entry: DeviceEntry
) -> list[dict[str, str]]:
    """List available event instances for a selected device and return them."""
    events = asyncio.run(fetch_event_instances(device_entry))
    if not events:
        print(f"No event instances found for {serial}.")  # noqa: T201
        return []

    print(f"\nEvent instances for {serial}:")  # noqa: T201
    for idx, ev in enumerate(events, 1):
        flags = []
        if ev["stateful"] == "True":
            flags.append("stateful")
        if ev["stateless"] == "True":
            flags.append("stateless")
        if ev["available"] == "True":
            flags.append("available")
        flag_str = ", ".join(flags) if flags else "none"
        print(f"  {idx}. {ev['name']} [{ev['topic']}] ({flag_str})")  # noqa: T201
    return events


def events_flow(serial: str, device_entry: DeviceEntry) -> None:
    """Event workflow: list instances and optionally start live listening."""
    while True:
        print(f"\nEvent options for {serial}:")  # noqa: T201
        print("  1. List event instances")  # noqa: T201
        print("  2. Listen to events (all topics)")  # noqa: T201
        print("  3. Listen to events (select topic)")  # noqa: T201
        print("  b. Back")  # noqa: T201
        print("  e. Exit")  # noqa: T201
        choice = input("Select option [1/2/3/b/e]: ").strip().lower()

        if choice == "e":
            print("Exiting.")  # noqa: T201
            raise SystemExit(0)
        if choice == "b":
            return

        if choice == "1":
            list_event_instances_flow(serial, device_entry)
            continue

        if choice == "2":
            _live_listen_flow(device_entry, topic_filter=None)
            continue

        if choice == "3":
            events = list_event_instances_flow(serial, device_entry)
            if not events:
                continue
            topic_choice = input("Enter event number to filter by: ").strip()
            try:
                topic_idx = int(topic_choice)
            except ValueError:
                print("Invalid selection.")  # noqa: T201
                continue
            if topic_idx < 1 or topic_idx > len(events):
                print("Invalid selection.")  # noqa: T201
                continue
            selected_topic = events[topic_idx - 1]["topic"]
            _live_listen_flow(device_entry, topic_filter=selected_topic)
            continue

        print("Invalid option. Please enter 1, 2, 3, b, or e.")  # noqa: T201


def _live_listen_flow(device_entry: DeviceEntry, topic_filter: str | None) -> None:
    """Start live event listening via the device stream manager."""
    credentials = get_device_credentials(device_entry)
    if credentials is None:
        print("Stored device config is incomplete. Please re-add the device.")  # noqa: T201
        return

    if topic_filter:
        print(f"\nListening for events on topic '{topic_filter}' (Ctrl+C to stop)...")  # noqa: T201
    else:
        print("\nListening for all events (Ctrl+C to stop)...")  # noqa: T201

    async def _run_listener() -> None:
        async with ClientSession() as session:
            config = Configuration(
                session=session,
                host=credentials["host"],
                username=credentials["username"],
                password=credentials["password"],
            )
            device = AxisDevice(config)

            def _on_event(event: object) -> None:
                print(f"  [event] {event}")  # noqa: T201

            unsubscribe = device.event.subscribe(
                callback=_on_event,
                id_filter=topic_filter,
            )
            stop_event = asyncio.Event()
            try:
                device.enable_events()
                await stop_event.wait()
            except asyncio.CancelledError:
                pass
            finally:
                unsubscribe()

    try:
        asyncio.run(_run_listener())
    except KeyboardInterrupt:
        print("\nStopped listening.")  # noqa: T201
    except RequestError as exc:
        print(f"Device request failed: {exc}")  # noqa: T201


# ---------------------------------------------------------------------------
# Phase 4 - Account management
# ---------------------------------------------------------------------------


import re  # noqa: E402

_USERNAME_RE = re.compile(r"^[a-zA-Z0-9]{1,14}$")


def _validate_username(username: str) -> str | None:
    """Return error message if username is invalid, else None."""
    if not _USERNAME_RE.match(username):
        return "Username must be 1-14 alphanumeric characters (a-z, A-Z, 0-9)."
    return None


def _select_privilege() -> SecondaryGroup | None:
    """Prompt user to choose a privilege level and return the SecondaryGroup."""
    options: list[tuple[str, SecondaryGroup]] = [
        ("Viewer", SecondaryGroup.VIEWER),
        ("Viewer + PTZ", SecondaryGroup.VIEWER_PTZ),
        ("Operator", SecondaryGroup.OPERATOR),
        ("Operator + PTZ", SecondaryGroup.OPERATOR_PTZ),
        ("Admin", SecondaryGroup.ADMIN),
        ("Admin + PTZ", SecondaryGroup.ADMIN_PTZ),
    ]
    print("\nPrivilege levels:")  # noqa: T201
    for idx, (label, _) in enumerate(options, 1):
        print(f"  {idx}. {label}")  # noqa: T201
    print("  b. Back")  # noqa: T201
    print("  e. Exit")  # noqa: T201
    sel = input("Select privilege [b/e]: ").strip().lower()
    if sel == "e":
        print("Exiting.")  # noqa: T201
        raise SystemExit(0)
    if sel == "b":
        return None
    try:
        idx = int(sel)
    except ValueError:
        print("Invalid selection.")  # noqa: T201
        return None
    if idx < 1 or idx > len(options):
        print("Invalid selection.")  # noqa: T201
        return None
    return options[idx - 1][1]


def _account_init_confirm(
    target_user: str,
    sgrp: SecondaryGroup,
    exists: bool,
) -> bool:
    """Prompt for create/update confirmation outside async context. Returns True to proceed."""
    if exists:
        answer = (
            input(
                f"User '{target_user}' already exists. "
                "Update password and privilege? (y/n): "
            )
            .strip()
            .lower()
        )
        if answer != "y":
            print("Account update aborted.")  # noqa: T201
            return False
    else:
        answer = (
            input(
                f"Create user '{target_user}' with "
                f"{sgrp.name.lower()} privileges? (y/n): "
            )
            .strip()
            .lower()
        )
        if answer != "y":
            print("Account creation aborted.")  # noqa: T201
            return False
    return True


async def _account_init_operation(
    device: AxisDevice,
    target_user: str,
    target_pwd: str,
    sgrp: SecondaryGroup,
    existing_users: Mapping[str, object],
) -> None:
    """Perform the actual create-or-update on the device inside a live session."""
    exists = target_user in existing_users
    if not _account_init_confirm(target_user, sgrp, exists):
        return
    if exists:
        await device.vapix.users.modify(target_user, pwd=target_pwd, sgrp=sgrp)
        print(f"User '{target_user}' updated.")  # noqa: T201
    else:
        await device.vapix.users.create(
            target_user,
            pwd=target_pwd,
            sgrp=sgrp,
            comment="Created via Axis CLI",
        )
        print(f"User '{target_user}' created.")  # noqa: T201


def account_management_flow(serial: str, device_entry: DeviceEntry) -> None:
    """Interactive account initialization and management workflow."""
    while True:
        print(f"\nAccount management for {serial}:")  # noqa: T201
        print("  1. List users")  # noqa: T201
        print("  2. Create or update user")  # noqa: T201
        print("  3. Delete user")  # noqa: T201
        print("  b. Back")  # noqa: T201
        print("  e. Exit")  # noqa: T201
        choice = input("Select option [1/2/3/b/e]: ").strip().lower()

        if choice == "e":
            print("Exiting.")  # noqa: T201
            raise SystemExit(0)
        if choice == "b":
            return

        if choice == "1":
            _list_users_flow(device_entry)
            continue

        if choice == "2":
            _create_or_update_user_flow(device_entry)
            continue

        if choice == "3":
            _delete_user_flow(device_entry)
            continue

        print("Invalid option. Please enter 1, 2, 3, b, or e.")  # noqa: T201


def _list_users_flow(device_entry: DeviceEntry) -> None:
    """Fetch and display all users on the device."""

    async def _op(device: AxisDevice) -> dict[str, object]:
        return dict(await device.vapix.users.list())

    users = asyncio.run(run_on_selected_device(device_entry, _op))
    if not users:
        print("No users found (or insufficient privileges).")  # noqa: T201
        return
    print("\nUsers:")  # noqa: T201
    for name, user in users.items():
        privs = str(getattr(user, "privileges", "unknown"))
        print(f"  - {name} ({privs})")  # noqa: T201


def _create_or_update_user_flow(device_entry: DeviceEntry) -> None:
    """Guided create/update user flow with explicit confirmation."""
    target_user = input("Username: ").strip()
    err = _validate_username(target_user)
    if err:
        print(f"Invalid username: {err}")  # noqa: T201
        return

    target_pwd = getpass.getpass("Password: ")
    if not (1 <= len(target_pwd) <= 64):
        print("Password must be 1-64 characters.")  # noqa: T201
        return

    sgrp = _select_privilege()
    if sgrp is None:
        return

    async def _op(device: AxisDevice) -> None:
        existing = await device.vapix.users.list()
        await _account_init_operation(device, target_user, target_pwd, sgrp, existing)

    try:
        asyncio.run(run_on_selected_device(device_entry, _op))
    except (Forbidden, PathNotFound) as exc:
        print(f"Access denied or unsupported on this device: {exc}")  # noqa: T201


def _delete_user_flow(device_entry: DeviceEntry) -> None:
    """Prompt for a username and delete it after explicit confirmation."""
    _list_users_flow(device_entry)
    target_user = input("\nUsername to delete: ").strip()
    if not target_user:
        print("No username provided.")  # noqa: T201
        return

    confirm = input(f"Permanently delete user '{target_user}'? (y/n): ").strip().lower()
    if confirm != "y":
        print("Deletion aborted.")  # noqa: T201
        return

    async def _op(device: AxisDevice) -> None:
        await device.vapix.users.delete(target_user)
        print(f"User '{target_user}' deleted.")  # noqa: T201

    try:
        asyncio.run(run_on_selected_device(device_entry, _op))
    except (Forbidden, PathNotFound) as exc:
        print(f"Access denied or unsupported on this device: {exc}")  # noqa: T201


# ---------------------------------------------------------------------------
# Device operations submenu
# ---------------------------------------------------------------------------


def selected_device_operations(serial: str, device_entry: DeviceEntry) -> None:
    """Run submenu operations for a selected registered device."""
    while True:
        print(f"\nDevice operations for {serial}:")  # noqa: T201
        print("  1. List supported APIs")  # noqa: T201
        print("  2. API drill-down")  # noqa: T201
        print("  3. Event instances & live listen")  # noqa: T201
        print("  4. Account management")  # noqa: T201
        print("  b. Back")  # noqa: T201
        print("  e. Exit")  # noqa: T201
        choice = input("Select option [1-4/b/e]: ").strip().lower()

        if choice == "1":
            list_supported_apis_flow(serial, device_entry)
            continue

        if choice == "2":
            api_drill_down_flow(device_entry)
            continue

        if choice == "3":
            events_flow(serial, device_entry)
            continue

        if choice == "4":
            account_management_flow(serial, device_entry)
            continue

        if choice == "b":
            return

        if choice == "e":
            print("Exiting.")  # noqa: T201
            raise SystemExit(0)

        print("Invalid option. Please enter 1, 2, 3, 4, b, or e.")  # noqa: T201


def main() -> None:
    """Run the interactive device registry CLI."""
    config_path = get_config_path()

    while True:
        devices = load_devices(config_path)
        print_registered_devices(devices)

        print("\nOptions:")  # noqa: T201
        print("  1. Add additional device")  # noqa: T201
        print("  2. Device operations")  # noqa: T201
        print("  e. Exit")  # noqa: T201
        choice = input("Select an option [1/2/e]: ").strip().lower()

        if choice == "e":
            print("Exiting.")  # noqa: T201
            raise SystemExit(0)

        if choice == "2":
            selected = select_device(devices)
            if selected is None:
                continue
            selected_serial, selected_entry = selected
            selected_device_operations(selected_serial, selected_entry)
            continue

        if choice != "1":
            print("Invalid option. Please enter 1, 2, or e.")  # noqa: T201
            continue

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
                continue

        config, serial, model, extra = asyncio.run(
            validate_and_fetch_device(device_info)
        )
        if config is None or serial is None or model is None or extra is None:
            continue

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
                continue

        devices[serial] = {
            "config": config_to_toml_dict(config),
            "model": model,
            "extra": extra,
        }
        save_devices(config_path, devices)
        print(f"Device '{serial}' registered/updated.")  # noqa: T201


if __name__ == "__main__":
    main()
