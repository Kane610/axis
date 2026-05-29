"""Axis CLI composition root and compatibility exports.

This module serves as the explicit bootstrap and import surface for the
plugin-pack based CLI architecture.
"""

# ruff: noqa: RUF022,TC003

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

from axis.cli.core.context import CliContext
from axis.cli.core.gateway import DeviceGateway
from axis.cli.core.registry import CommandRegistry
from axis.cli.core.router import CliRouter
from axis.cli.packs import (
    accounts as accounts_pack,
    api as api_pack,
    devices as devices_pack,
    events as events_pack,
    navigation as navigation_pack,
)

DeviceEntry = devices_pack.DeviceEntry
DeviceStore = devices_pack.DeviceStore

# Compatibility exports from packs
get_config_path = devices_pack.get_config_path
load_devices = devices_pack.load_devices
save_devices = devices_pack.save_devices
to_toml_compatible = devices_pack.to_toml_compatible
fetch_device_serial_and_extra = devices_pack.fetch_device_serial_and_extra
extract_model_number = devices_pack.extract_model_number
extract_serial_number = devices_pack.extract_serial_number
prompt_for_device = devices_pack.prompt_for_device
config_to_toml_dict = devices_pack.config_to_toml_dict
_format_device_label = devices_pack._format_device_label
validate_and_fetch_device = devices_pack.validate_and_fetch_device
print_registered_devices = devices_pack.print_registered_devices
migrate_unknown_entry = devices_pack.migrate_unknown_entry
find_serial_by_host = devices_pack.find_serial_by_host
select_device = devices_pack.select_device
get_device_credentials = devices_pack.get_device_credentials
run_on_selected_device = devices_pack.run_on_selected_device

fetch_supported_apis = api_pack.fetch_supported_apis
list_supported_apis_flow = api_pack.list_supported_apis_flow
run_api_read_action = api_pack.run_api_read_action
api_drill_down_flow = api_pack.api_drill_down_flow

fetch_event_instances = events_pack.fetch_event_instances
list_event_instances_flow = events_pack.list_event_instances_flow
events_flow = events_pack.events_flow
_live_listen_flow = events_pack._live_listen_flow

_validate_username = accounts_pack._validate_username
_select_privilege = accounts_pack._select_privilege
_account_init_confirm = accounts_pack._account_init_confirm
_account_init_operation = accounts_pack._account_init_operation
account_management_flow = accounts_pack.account_management_flow
_list_users_flow = accounts_pack._list_users_flow
_create_or_update_user_flow = accounts_pack._create_or_update_user_flow
_delete_user_flow = accounts_pack._delete_user_flow

selected_device_operations = navigation_pack.selected_device_operations


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Axis interactive CLI")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable verbose debug output for raw device/API responses.",
    )
    return parser.parse_args(argv)


def _debug_enabled_from_env() -> bool:
    value = os.getenv("AXIS_CLI_DEBUG", "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def _configure_logging(debug_enabled: bool) -> None:
    loglevel = logging.DEBUG if debug_enabled else logging.INFO
    logging.basicConfig(format="%(message)s", level=loglevel, force=True)


def compose_builtin_packs(registry: CommandRegistry, router: CliRouter) -> None:
    """Register built-in CLI packs explicitly from a single composition root."""
    devices_pack.register(registry, router)
    api_pack.register(registry, router)
    events_pack.register(registry, router)
    accounts_pack.register(registry, router)
    navigation_pack.register(registry, router)


def build_cli_runtime(config_path: Path) -> CliContext:
    """Create shared runtime context for the CLI process."""
    registry = CommandRegistry()
    router = CliRouter()
    compose_builtin_packs(registry, router)
    return CliContext(config_path=config_path, device_gateway=DeviceGateway())


def main(*, debug: bool | None = None) -> None:
    """Run the interactive device registry CLI."""
    debug_enabled = _debug_enabled_from_env() if debug is None else debug
    _configure_logging(debug_enabled)

    if debug_enabled:
        os.environ["AXIS_CLI_DEBUG"] = "1"
        print("Debug mode enabled. Verbose responses will be shown.")  # noqa: T201

    config_path = get_config_path()
    _runtime = build_cli_runtime(config_path)
    _ = _runtime
    while True:
        try:
            navigation_pack.run_main_loop(config_path)
        except KeyboardInterrupt:
            print("\nInterrupted. Use 'e' to exit.")  # noqa: T201
            continue


__all__ = [
    "DeviceEntry",
    "DeviceStore",
    "compose_builtin_packs",
    "build_cli_runtime",
    "main",
    "get_config_path",
    "load_devices",
    "save_devices",
    "to_toml_compatible",
    "fetch_device_serial_and_extra",
    "extract_model_number",
    "extract_serial_number",
    "prompt_for_device",
    "config_to_toml_dict",
    "_format_device_label",
    "validate_and_fetch_device",
    "print_registered_devices",
    "migrate_unknown_entry",
    "find_serial_by_host",
    "select_device",
    "get_device_credentials",
    "run_on_selected_device",
    "fetch_supported_apis",
    "list_supported_apis_flow",
    "run_api_read_action",
    "api_drill_down_flow",
    "fetch_event_instances",
    "list_event_instances_flow",
    "events_flow",
    "_live_listen_flow",
    "_validate_username",
    "_select_privilege",
    "_account_init_confirm",
    "_account_init_operation",
    "account_management_flow",
    "_list_users_flow",
    "_create_or_update_user_flow",
    "_delete_user_flow",
    "selected_device_operations",
]


if __name__ == "__main__":
    args = _parse_args()
    main(debug=args.debug)
