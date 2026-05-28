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
from typing import Any

from aiohttp import ClientSession
import tomli
import tomli_w

from axis.device import AxisDevice
from axis.errors import RequestError
from axis.models.configuration import Configuration

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
) -> tuple[str, dict[str, Any]]:
    """Fetch device serial and extra info from a device."""
    device = AxisDevice(config)
    info = await device.vapix.basic_device_info.get_all_properties()
    serial = extract_serial_number(info)
    return serial, info


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


async def validate_and_fetch_device(
    device_info: dict[str, str],
) -> tuple[Configuration | None, str | None, dict[str, Any] | None]:
    """Validate a device and fetch serial/extra info."""
    try:
        async with ClientSession() as session:
            config = Configuration(
                session=session,
                host=device_info["host"],
                username=device_info["username"],
                password=device_info["password"],
            )
            serial, extra = await fetch_device_serial_and_extra(config)
            return config, serial, extra
    except RequestError as exc:
        print(f"Failed to connect to device: {exc}")  # noqa: T201
        print("Please verify host reachability and credentials, then try again.")  # noqa: T201
        return None, None, None
    except (ValueError, KeyError, OSError) as exc:
        print(f"Failed to fetch device info: {exc}")  # noqa: T201
        print("Please check your credentials and try again.")  # noqa: T201
        return None, None, None


def print_registered_devices(devices: DeviceStore) -> None:
    """Print the currently registered devices."""
    if not devices:
        print("\nNo devices registered yet.")  # noqa: T201
        return

    print("\nRegistered devices:")  # noqa: T201
    for idx, (serial, device_data) in enumerate(devices.items(), 1):
        host = str(device_data.get("config", {}).get("host", "<unknown>"))
        print(f"  {idx}. {serial} ({host})")  # noqa: T201


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


def main() -> None:
    """Run the interactive device registry CLI."""
    config_path = get_config_path()

    while True:
        devices = load_devices(config_path)
        print_registered_devices(devices)

        print("\nOptions:")  # noqa: T201
        print("  1. Add additional device")  # noqa: T201
        print("  2. Exit")  # noqa: T201
        choice = input("Select an option [1/2]: ").strip()

        if choice == "2":
            print("Exiting.")  # noqa: T201
            raise SystemExit(0)

        if choice != "1":
            print("Invalid option. Please enter 1 or 2.")  # noqa: T201
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

        config, serial, extra = asyncio.run(validate_and_fetch_device(device_info))
        if config is None or serial is None or extra is None:
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
            "extra": extra,
        }
        save_devices(config_path, devices)
        print(f"Device '{serial}' registered/updated.")  # noqa: T201


if __name__ == "__main__":
    main()
