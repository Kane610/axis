"""Direct-import tests for axis.cli.main Phase 3+4 helpers.

Covers event-instance listing, account management confirm/validate helpers,
and operations that orchestrate device calls via mocked AxisDevice.
"""

from __future__ import annotations

import asyncio as _asyncio
import logging
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from axis.cli.core.contracts import CommandResult
from axis.cli.main import (
    DeviceEntry,
    _account_init_confirm,
    _create_or_update_user_async,
    _delete_user_async,
    _list_users_async,
    _select_privilege,
    _validate_username,
    account_management_async,
    api_drill_down_async,
    events_menu_async,
    list_event_instances_async,
    list_supported_apis_async,
    main,
    run_on_selected_device,
    selected_device_operations,
    validate_and_fetch_device,
)
from axis.errors import RequestError
from axis.models.pwdgrp_cgi import SecondaryGroup

# ---------------------------------------------------------------------------
# _validate_username
# ---------------------------------------------------------------------------


def test_validate_username_valid() -> None:
    """Valid usernames pass without an error message."""
    assert _validate_username("admin") is None
    assert _validate_username("a" * 14) is None
    assert _validate_username("A1b2C3") is None


def test_validate_username_empty() -> None:
    """Empty string is invalid."""
    assert _validate_username("") is not None


def test_validate_username_too_long() -> None:
    """More than 14 characters is invalid."""
    assert _validate_username("a" * 15) is not None


def test_validate_username_special_chars() -> None:
    """Special characters are invalid."""
    assert _validate_username("bad@user") is not None
    assert _validate_username("has space") is not None


# ---------------------------------------------------------------------------
# _account_init_confirm
# ---------------------------------------------------------------------------


def test_account_init_confirm_create_yes() -> None:
    """Returns True when user confirms creation."""
    with patch("builtins.input", return_value="y"):
        result = _account_init_confirm("testuser", SecondaryGroup.VIEWER, exists=False)
    assert result is True


def test_account_init_confirm_create_no() -> None:
    """Returns False when user declines creation."""
    with patch("builtins.input", return_value="n"):
        result = _account_init_confirm("testuser", SecondaryGroup.VIEWER, exists=False)
    assert result is False


def test_account_init_confirm_update_yes() -> None:
    """Returns True when user confirms update."""
    with patch("builtins.input", return_value="y"):
        result = _account_init_confirm("testuser", SecondaryGroup.ADMIN, exists=True)
    assert result is True


def test_account_init_confirm_update_no() -> None:
    """Returns False when user declines update."""
    with patch("builtins.input", return_value="n"):
        result = _account_init_confirm("testuser", SecondaryGroup.ADMIN, exists=True)
    assert result is False


# ---------------------------------------------------------------------------
# list_event_instances_async (mocked device)
# ---------------------------------------------------------------------------


def _make_device_entry() -> DeviceEntry:
    """Return a minimal device entry for testing."""
    return {
        "config": {
            "host": "192.168.1.1",
            "username": "admin",
            "password": "pass",
        }
    }


def _mock_asyncio_run_return(value: object):
    """Create asyncio.run side effect that closes incoming coroutines."""

    def _runner(coro: object) -> object:
        if _asyncio.iscoroutine(coro):
            coro.close()
        return value

    return _runner


def _make_event_instance(
    topic: str = "tnsaxis:HardwareFailure/Fan",
    name: str = "Fan failure",
    stateful: bool = True,
    stateless: bool = False,
    is_available: bool = True,
) -> MagicMock:
    ev = MagicMock()
    ev.topic = topic
    ev.name = name
    ev.stateful = stateful
    ev.stateless = stateless
    ev.is_available = is_available
    return ev


def test_list_event_instances_async_empty(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Prints 'No event instances' when none are returned."""
    with patch(
        "axis.cli.packs.events.fetch_event_instances",
        new=AsyncMock(return_value=[]),
    ):
        result = _asyncio.run(list_event_instances_async("SN1", _make_device_entry()))
    assert result == []
    out = capsys.readouterr().out
    assert "No event instances" in out


def test_list_event_instances_async_with_results(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Prints event list when instances are returned."""
    fake_events = [
        {
            "topic": "tnsaxis:HardwareFailure/Fan",
            "name": "Fan failure",
            "stateful": "True",
            "stateless": "False",
            "available": "True",
        }
    ]
    with patch(
        "axis.cli.packs.events.fetch_event_instances",
        new=AsyncMock(return_value=fake_events),
    ):
        result = _asyncio.run(list_event_instances_async("SN1", _make_device_entry()))
    assert len(result) == 1
    out = capsys.readouterr().out
    assert "Event instances for" in out
    assert "192.168.1.1" in out
    assert "mac=SN1" in out
    assert "#" in out
    assert "name" in out
    assert "topic" in out
    assert "state" in out
    assert "available" in out
    assert "Fan failure" in out
    assert "tnsaxis:HardwareFailure/Fan" in out


def test_list_event_instances_async_with_empty_name(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Uses a fallback label when event name is empty."""
    fake_events = [
        {
            "topic": "tns1:Device/Trigger/DigitalInput",
            "name": "",
            "stateful": "True",
            "stateless": "False",
            "available": "True",
        }
    ]
    with patch(
        "axis.cli.packs.events.fetch_event_instances",
        new=AsyncMock(return_value=fake_events),
    ):
        result = _asyncio.run(list_event_instances_async("SN1", _make_device_entry()))
    assert len(result) == 1
    out = capsys.readouterr().out
    assert "<unnamed>" in out


# ---------------------------------------------------------------------------
# events_menu_async navigation
# ---------------------------------------------------------------------------


def test_events_menu_async_exit(capsys: pytest.CaptureFixture[str]) -> None:
    """Selecting 'e' raises SystemExit."""
    with (
        patch("builtins.input", side_effect=["e"]),
        pytest.raises(SystemExit),
    ):
        _asyncio.run(events_menu_async("SN1", _make_device_entry()))


def test_events_menu_async_back(capsys: pytest.CaptureFixture[str]) -> None:
    """Selecting 'b' exits immediately."""
    with patch("builtins.input", side_effect=["b"]):
        _asyncio.run(events_menu_async("SN1", _make_device_entry()))


def test_events_menu_async_invalid_then_back(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Invalid input shows message then 'b' exits."""
    with patch("builtins.input", side_effect=["9", "b"]):
        _asyncio.run(events_menu_async("SN1", _make_device_entry()))
    out = capsys.readouterr().out
    assert "Invalid" in out


# ---------------------------------------------------------------------------
# account_management_async navigation
# ---------------------------------------------------------------------------


def test_account_management_async_exit(capsys: pytest.CaptureFixture[str]) -> None:
    """Selecting 'e' raises SystemExit."""
    with (
        patch("builtins.input", side_effect=["e"]),
        pytest.raises(SystemExit),
    ):
        _asyncio.run(account_management_async("SN1", _make_device_entry()))


def test_account_management_async_back(capsys: pytest.CaptureFixture[str]) -> None:
    """Selecting 'b' exits without calling any account operation."""
    with patch("builtins.input", side_effect=["b"]):
        _asyncio.run(account_management_async("SN1", _make_device_entry()))
    out = capsys.readouterr().out
    assert "Account management for" in out
    assert "192.168.1.1" in out
    assert "mac=SN1" in out


def test_account_management_async_invalid_then_back(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Invalid input shows message; then 'b' exits."""
    with patch("builtins.input", side_effect=["9", "b"]):
        _asyncio.run(account_management_async("SN1", _make_device_entry()))
    out = capsys.readouterr().out
    assert "Invalid" in out


# ---------------------------------------------------------------------------
# _list_users_async
# ---------------------------------------------------------------------------


def test_list_users_async_empty(capsys: pytest.CaptureFixture[str]) -> None:
    """Prints 'No users found' when run_on_selected_device returns None."""
    with patch(
        "axis.cli.packs.accounts.run_on_selected_device",
        new=AsyncMock(return_value=None),
    ):
        _asyncio.run(_list_users_async(_make_device_entry()))
    out = capsys.readouterr().out
    assert "No users" in out


def test_list_users_async_with_users(capsys: pytest.CaptureFixture[str]) -> None:
    """Prints usernames when users are returned."""
    user = MagicMock()
    user.privileges = SecondaryGroup.VIEWER
    fake_users = {"vieweruser": user}
    with patch(
        "axis.cli.packs.accounts.run_on_selected_device",
        new=AsyncMock(return_value=fake_users),
    ):
        _asyncio.run(_list_users_async(_make_device_entry()))
    out = capsys.readouterr().out
    assert "vieweruser" in out


# ---------------------------------------------------------------------------
# _delete_user_async
# ---------------------------------------------------------------------------


def test_delete_user_async_aborted(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Deletion aborted when user types 'n' at confirmation."""
    user = MagicMock()
    user.privileges = SecondaryGroup.VIEWER
    fake_users = {"vieweruser": user}
    with (
        patch(
            "axis.cli.packs.accounts.run_on_selected_device",
            new=AsyncMock(side_effect=[fake_users, None]),
        ),
        patch("builtins.input", side_effect=["vieweruser", "n"]),
    ):
        _asyncio.run(_delete_user_async(_make_device_entry()))
    out = capsys.readouterr().out
    assert "aborted" in out.lower()


def test_delete_user_async_empty_input(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Does nothing when an empty username is entered."""
    user = MagicMock()
    user.privileges = SecondaryGroup.VIEWER
    fake_users: dict[str, object] = {"vieweruser": user}
    with (
        patch(
            "axis.cli.packs.accounts.run_on_selected_device",
            new=AsyncMock(return_value=fake_users),
        ),
        patch("builtins.input", side_effect=["", ""]),
    ):
        _asyncio.run(_delete_user_async(_make_device_entry()))
    out = capsys.readouterr().out
    assert "No username" in out


# ---------------------------------------------------------------------------
# validate_and_fetch_device
# ---------------------------------------------------------------------------


def test_validate_and_fetch_device_request_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Returns (None, None, None, None) and prints message on RequestError."""
    with (
        patch(
            "axis.cli.packs.devices.fetch_device_serial_and_extra",
            side_effect=RequestError("timeout"),
        ),
        patch("axis.cli.packs.devices.ClientSession"),
    ):
        result = _asyncio.run(
            validate_and_fetch_device(
                {"host": "192.168.1.1", "username": "u", "password": "p"}
            )
        )
    assert result == (None, None, None, None)
    out = capsys.readouterr().out
    assert "Failed to connect" in out


def test_validate_and_fetch_device_value_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Returns (None, None, None, None) and prints message on ValueError."""
    with (
        patch(
            "axis.cli.packs.devices.fetch_device_serial_and_extra",
            side_effect=ValueError("bad value"),
        ),
        patch("axis.cli.packs.devices.ClientSession"),
    ):
        result = _asyncio.run(
            validate_and_fetch_device(
                {"host": "192.168.1.1", "username": "u", "password": "p"}
            )
        )
    assert result == (None, None, None, None)
    out = capsys.readouterr().out
    assert "Failed to fetch" in out


def test_validate_and_fetch_device_retries_with_companion(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Retries with companion mode on connection-style failure."""
    companion_attempts: list[bool] = []

    async def side_effect(config: object) -> tuple[str, str, dict[str, object]]:
        companion_attempts.append(bool(getattr(config, "is_companion", False)))
        if companion_attempts == [False]:
            msg = "timeout"
            raise RequestError(msg)
        return "SN1", "P3245", {"ok": True}

    with (
        patch(
            "axis.cli.packs.devices.fetch_device_serial_and_extra",
            side_effect=side_effect,
        ),
        patch("axis.cli.packs.devices.ClientSession"),
    ):
        config, serial, model, extra = _asyncio.run(
            validate_and_fetch_device(
                {"host": "192.168.1.1", "username": "u", "password": "p"}
            )
        )

    assert config is not None
    assert config.is_companion is True
    assert serial == "SN1"
    assert model == "P3245"
    assert extra == {"ok": True}
    assert companion_attempts == [False, True]
    out = capsys.readouterr().out
    assert "Retrying with companion mode enabled" in out


def test_validate_and_fetch_device_debug_failure_details(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Debug mode prints attempt and failure details for both retries."""
    with (
        patch.dict(os.environ, {"AXIS_CLI_DEBUG": "1"}, clear=True),
        patch(
            "axis.cli.packs.devices.fetch_device_serial_and_extra",
            side_effect=RequestError("timeout"),
        ),
        patch("axis.cli.packs.devices.ClientSession"),
    ):
        result = _asyncio.run(
            validate_and_fetch_device(
                {"host": "10.0.0.113", "username": "root", "password": "p"}
            )
        )

    assert result == (None, None, None, None)
    out = capsys.readouterr().out
    assert "[debug] device validation attempt" in out
    assert "is_companion': False" in out
    assert "is_companion': True" in out
    assert "error_type': 'RequestError'" in out


# ---------------------------------------------------------------------------
# run_on_selected_device
# ---------------------------------------------------------------------------


def test_run_on_selected_device_incomplete_credentials(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Returns None when device_entry has no host."""
    entry: DeviceEntry = {"config": {"host": "", "username": "admin"}}
    result = _asyncio.run(run_on_selected_device(entry, AsyncMock(return_value="x")))
    assert result is None
    out = capsys.readouterr().out
    assert "incomplete" in out


def test_run_on_selected_device_request_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Returns None and prints message on RequestError."""
    op = AsyncMock(side_effect=RequestError("refused"))
    with (
        patch("axis.cli.packs.devices.AxisDevice"),
        patch("axis.cli.packs.devices.ClientSession"),
    ):
        result = _asyncio.run(run_on_selected_device(_make_device_entry(), op))
    assert result is None
    out = capsys.readouterr().out
    assert "request failed" in out.lower()


# ---------------------------------------------------------------------------
# list_supported_apis_async
# ---------------------------------------------------------------------------


def test_list_supported_apis_async_empty(capsys: pytest.CaptureFixture[str]) -> None:
    """Prints 'No APIs discovered' when none returned."""
    with patch(
        "axis.cli.packs.api.fetch_supported_apis", new=AsyncMock(return_value=[])
    ):
        _asyncio.run(list_supported_apis_async("SN1", _make_device_entry()))
    out = capsys.readouterr().out
    assert "No APIs" in out


def test_list_supported_apis_async_with_apis(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Prints API table when APIs are returned."""
    fake_apis = [
        {
            "id": "basic-device-info",
            "name": "Basic Device Info",
            "version": "2.0",
            "status": "Released",
        },
    ]
    with patch(
        "axis.cli.packs.api.fetch_supported_apis",
        new=AsyncMock(return_value=fake_apis),
    ):
        _asyncio.run(list_supported_apis_async("SN1", _make_device_entry()))
    out = capsys.readouterr().out
    assert "Supported APIs for" in out
    assert "192.168.1.1" in out
    assert "mac=SN1" in out
    assert "#" in out
    assert "id" in out
    assert "name" in out
    assert "version" in out
    assert "status" in out
    assert "basic-device-info" in out


# ---------------------------------------------------------------------------
# api_drill_down_async
# ---------------------------------------------------------------------------


def test_api_drill_down_async_no_apis(capsys: pytest.CaptureFixture[str]) -> None:
    """Returns immediately when no interfaces are discovered."""
    with patch(
        "axis.cli.packs.api.fetch_vapix_interfaces", new=AsyncMock(return_value=[])
    ):
        _asyncio.run(api_drill_down_async(_make_device_entry()))
    out = capsys.readouterr().out
    assert "No interfaces" in out


def test_api_drill_down_async_back(capsys: pytest.CaptureFixture[str]) -> None:
    """Typing 'b' exits the drill-down immediately."""
    fake_interfaces = [
        {
            "name": "basic_device_info",
            "api_id": "basic-device-info",
            "api_version": "1",
            "supported": True,
            "initialized": False,
            "items": 0,
        },
    ]
    with (
        patch(
            "axis.cli.packs.api.fetch_vapix_interfaces",
            new=AsyncMock(return_value=fake_interfaces),
        ),
        patch("builtins.input", return_value="b"),
    ):
        _asyncio.run(api_drill_down_async(_make_device_entry()))


def test_api_drill_down_async_prints_normalized_columns(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Drill-down list prints fixed-width columns for easier comparison."""
    fake_interfaces = [
        {
            "name": "api_discovery",
            "api_id": "api-discovery",
            "api_version": "1.0",
            "listed": True,
            "probe_attempted": True,
            "probe_succeeded": True,
            "supported": True,
            "initialized": False,
            "items": 0,
        },
        {
            "name": "event_instances",
            "api_id": "",
            "api_version": "",
            "listed": False,
            "probe_attempted": True,
            "probe_succeeded": True,
            "supported": False,
            "initialized": False,
            "items": 3,
        },
    ]
    with (
        patch(
            "axis.cli.packs.api.fetch_vapix_interfaces",
            new=AsyncMock(return_value=fake_interfaces),
        ),
        patch("builtins.input", return_value="b"),
    ):
        _asyncio.run(api_drill_down_async(_make_device_entry()))

    out = capsys.readouterr().out
    assert "#" in out
    assert "name" in out
    assert "api" in out
    assert "adv" in out
    assert "probe" in out
    assert "usable" in out
    assert "init" in out
    assert "items" in out


def test_api_drill_down_async_selected_details_truth_fields(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Selected interface details include listed/probe/supported truth fields."""
    fake_interfaces = [
        {
            "name": "object_analytics",
            "api_id": "",
            "api_version": "",
            "listed": False,
            "probe_attempted": True,
            "probe_succeeded": True,
            "supported": True,
            "initialized": True,
            "items": 1,
        },
    ]
    with (
        patch(
            "axis.cli.packs.api.fetch_vapix_interfaces",
            new=AsyncMock(return_value=fake_interfaces),
        ),
        patch("builtins.input", side_effect=["1", "b", "b"]),
    ):
        _asyncio.run(api_drill_down_async(_make_device_entry()))

    out = capsys.readouterr().out
    assert "Listed:" in out
    assert "Probe Attempted:" in out
    assert "Probe Succeeded:" in out
    assert "Supported:" in out


def test_api_drill_down_async_invalid_index(capsys: pytest.CaptureFixture[str]) -> None:
    """Invalid index shows error then 'b' exits."""
    fake_interfaces = [
        {
            "name": "basic_device_info",
            "api_id": "basic-device-info",
            "api_version": "1",
            "supported": True,
            "initialized": False,
            "items": 0,
        },
    ]
    with (
        patch(
            "axis.cli.packs.api.fetch_vapix_interfaces",
            new=AsyncMock(return_value=fake_interfaces),
        ),
        patch("builtins.input", side_effect=["99", "b"]),
    ):
        _asyncio.run(api_drill_down_async(_make_device_entry()))
    out = capsys.readouterr().out
    assert "Invalid" in out


def test_api_drill_down_async_non_numeric(capsys: pytest.CaptureFixture[str]) -> None:
    """Non-numeric input shows error then 'b' exits."""
    fake_interfaces = [
        {
            "name": "basic_device_info",
            "api_id": "basic-device-info",
            "api_version": "1",
            "supported": True,
            "initialized": False,
            "items": 0,
        },
    ]
    with (
        patch(
            "axis.cli.packs.api.fetch_vapix_interfaces",
            new=AsyncMock(return_value=fake_interfaces),
        ),
        patch("builtins.input", side_effect=["abc", "b"]),
    ):
        _asyncio.run(api_drill_down_async(_make_device_entry()))
    out = capsys.readouterr().out
    assert "Invalid" in out


def test_api_drill_down_async_action_back(capsys: pytest.CaptureFixture[str]) -> None:
    """Selecting interface then action 'b' loops back to interface list."""
    fake_interfaces = [
        {
            "name": "basic_device_info",
            "api_id": "basic-device-info",
            "api_version": "1",
            "supported": True,
            "initialized": False,
            "items": 0,
        },
    ]
    with (
        patch(
            "axis.cli.packs.api.fetch_vapix_interfaces",
            new=AsyncMock(return_value=fake_interfaces),
        ),
        patch("builtins.input", side_effect=["1", "b", "b"]),
    ):
        _asyncio.run(api_drill_down_async(_make_device_entry()))


def test_api_drill_down_async_show_all_data_stays_on_selected_interface(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Show-all-data returns to the selected interface actions."""
    fake_interfaces = [
        {
            "name": "temperature_control",
            "api_id": "temperaturecontrol",
            "api_version": "1",
            "supported": True,
            "initialized": True,
            "items": 3,
        },
    ]

    async def _fetch_interfaces(_: DeviceEntry) -> list[dict[str, str | bool | int]]:
        return fake_interfaces

    async def _read_interface_data(
        _: DeviceEntry,
        _name: str,
        _traversal_path: str | None = None,
    ) -> None:
        return None

    with (
        patch("axis.cli.packs.api.fetch_vapix_interfaces", _fetch_interfaces),
        patch("axis.cli.packs.api.run_api_read_action", _read_interface_data),
        patch("builtins.input", side_effect=["1", "1", "b", "b"]),
    ):
        _asyncio.run(api_drill_down_async(_make_device_entry()))

    out = capsys.readouterr().out
    assert out.count("Selected interface:") == 1
    assert out.count("Interface actions:") == 2


def test_api_drill_down_async_action_invalid(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Invalid action choice shows message then 'b' exits."""
    fake_interfaces = [
        {
            "name": "basic_device_info",
            "api_id": "basic-device-info",
            "api_version": "1",
            "supported": True,
            "initialized": False,
            "items": 0,
        },
    ]
    with (
        patch(
            "axis.cli.packs.api.fetch_vapix_interfaces",
            new=AsyncMock(return_value=fake_interfaces),
        ),
        patch("builtins.input", side_effect=["1", "9", "b", "b"]),
    ):
        _asyncio.run(api_drill_down_async(_make_device_entry()))
    out = capsys.readouterr().out
    assert "Invalid" in out


# ---------------------------------------------------------------------------
# selected_device_operations
# ---------------------------------------------------------------------------


def test_selected_device_operations_exit(capsys: pytest.CaptureFixture[str]) -> None:
    """Selecting 'e' raises SystemExit."""
    with (
        patch("builtins.input", side_effect=["e"]),
        pytest.raises(SystemExit),
    ):
        selected_device_operations("SN1", _make_device_entry())


def test_selected_device_operations_back(capsys: pytest.CaptureFixture[str]) -> None:
    """Selecting 'b' returns without calling any operation."""
    with patch("builtins.input", return_value="b"):
        selected_device_operations("SN1", _make_device_entry())


def test_selected_device_operations_invalid_then_back(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Invalid option prints message; 'b' exits."""
    with patch("builtins.input", side_effect=["9", "b"]):
        selected_device_operations("SN1", _make_device_entry())
    out = capsys.readouterr().out
    assert "Invalid" in out


def test_selected_device_operations_list_apis(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Option '1' executes async API listing via asyncio.run."""
    with (
        patch("axis.cli.packs.navigation.asyncio") as mock_asyncio,
        patch("builtins.input", side_effect=["1", "b"]),
    ):
        mock_asyncio.run.side_effect = _mock_asyncio_run_return(None)
        selected_device_operations("SN1", _make_device_entry())
    assert mock_asyncio.run.call_count == 1


def test_selected_device_operations_api_drilldown(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Option '2' executes async API drill-down via asyncio.run."""
    with (
        patch("axis.cli.packs.navigation.asyncio") as mock_asyncio,
        patch("builtins.input", side_effect=["2", "b"]),
    ):
        mock_asyncio.run.side_effect = _mock_asyncio_run_return(None)
        selected_device_operations("SN1", _make_device_entry())
    assert mock_asyncio.run.call_count == 1


def test_selected_device_operations_events(capsys: pytest.CaptureFixture[str]) -> None:
    """Option '3' executes async events menu via asyncio.run."""
    with (
        patch("axis.cli.packs.navigation.asyncio") as mock_asyncio,
        patch("builtins.input", side_effect=["3", "b"]),
    ):
        mock_asyncio.run.side_effect = _mock_asyncio_run_return(None)
        selected_device_operations("SN1", _make_device_entry())
    assert mock_asyncio.run.call_count == 1


def test_selected_device_operations_accounts(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Option '4' executes async account menu via asyncio.run."""
    with (
        patch("axis.cli.packs.navigation.asyncio") as mock_asyncio,
        patch("builtins.input", side_effect=["4", "b"]),
    ):
        mock_asyncio.run.side_effect = _mock_asyncio_run_return(None)
        selected_device_operations("SN1", _make_device_entry())
    assert mock_asyncio.run.call_count == 1


# ---------------------------------------------------------------------------
# main() key paths
# ---------------------------------------------------------------------------


def test_main_exit(capsys: pytest.CaptureFixture[str]) -> None:
    """Selecting 'e' exits the main loop via SystemExit."""
    with (
        patch("axis.cli.packs.navigation.load_devices", return_value={}),
        patch("axis.cli.packs.navigation.get_config_path"),
        patch("builtins.input", return_value="e"),
        pytest.raises(SystemExit),
    ):
        main()


def test_main_invalid_option(capsys: pytest.CaptureFixture[str]) -> None:
    """Invalid option prints message; then 'e' exits."""
    with (
        patch("axis.cli.packs.navigation.load_devices", return_value={}),
        patch("axis.cli.packs.navigation.get_config_path"),
        patch("builtins.input", side_effect=["9", "e"]),
        pytest.raises(SystemExit),
    ):
        main()
    out = capsys.readouterr().out
    assert "Invalid" in out


def test_main_device_operations_no_devices(capsys: pytest.CaptureFixture[str]) -> None:
    """Option '3' with empty registry selects nothing and loops back to exit."""
    with (
        patch("axis.cli.packs.devices.load_devices", return_value={}),
        patch("builtins.input", side_effect=["1", "3", "e"]),
        pytest.raises(SystemExit),
    ):
        main()


def test_main_device_operations_runs_submenu(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Main route reaches device operations when a device is selected."""
    fake_entry = _make_device_entry()
    with (
        patch("axis.cli.packs.devices.load_devices", return_value={"SN1": fake_entry}),
        patch("axis.cli.packs.devices.select_device", return_value=("SN1", fake_entry)),
        patch("builtins.input", side_effect=["1", "3", "e"]),
        pytest.raises(SystemExit),
    ):
        main()
    out = capsys.readouterr().out
    assert "Device operations for" in out


def test_main_discovery_no_devices_found(capsys: pytest.CaptureFixture[str]) -> None:
    """Option '2' returns to menu when no discoverable devices are found."""
    with (
        patch("axis.cli.packs.devices.load_devices", return_value={}),
        patch(
            "axis.cli.packs.devices.discover_axis_devices",
            new=AsyncMock(return_value=[]),
        ),
        patch("axis.cli.packs.devices.select_discovered_device", return_value=None),
        patch("builtins.input", side_effect=["1", "2", "e"]),
        pytest.raises(SystemExit),
    ):
        main()


def test_main_discovery_filters_already_registered_before_selection(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Option '2' excludes already-registered devices before listing selection."""
    existing_entry = {
        "config": {
            "host": "10.0.0.211",
            "username": "admin",
            "password": "pass",
        }
    }
    discovered = [
        {
            "host": "169.254.24.20",
            "name": "Already added via serial",
            "macaddress": "B8A44F909AFD",
        },
        {
            "host": "10.0.0.250",
            "name": "New device",
            "macaddress": "B8A44FEEB430",
        },
    ]

    with (
        patch(
            "axis.cli.packs.devices.load_devices",
            return_value={"B8A44F909AFD": existing_entry},
        ),
        patch(
            "axis.cli.packs.devices.discover_axis_devices",
            new=AsyncMock(return_value=discovered),
        ),
        patch(
            "axis.cli.packs.devices.select_discovered_device",
            return_value=None,
        ) as mock_select_discovered,
        patch("builtins.input", side_effect=["1", "2", "e"]),
        pytest.raises(SystemExit),
    ):
        main()

    filtered_arg = mock_select_discovered.call_args.args[0]
    assert filtered_arg == [
        {
            "host": "10.0.0.250",
            "name": "New device",
            "macaddress": "B8A44FEEB430",
        }
    ]


def test_main_discovery_registers_selected_device(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Option '2' can discover, validate, and persist a selected device."""
    discovered = [
        {
            "host": "10.0.0.22",
            "name": "Axis 10.0.0.22",
            "macaddress": "00408c112233",
        }
    ]

    with (
        patch("axis.cli.packs.devices.load_devices", return_value={}),
        patch(
            "axis.cli.packs.devices.select_discovered_device",
            return_value=discovered[0],
        ),
        patch(
            "axis.cli.packs.devices.discover_axis_devices",
            new=AsyncMock(return_value=discovered),
        ),
        patch(
            "axis.cli.packs.devices.register_or_update_device_async",
            new=AsyncMock(return_value=CommandResult(status="ok", message="ok")),
        ),
        patch("axis.cli.packs.devices.save_devices") as mock_save,
        patch("axis.cli.core.io.getpass", return_value="pass"),
        patch("builtins.input", side_effect=["1", "2", "admin", "e"]),
        pytest.raises(SystemExit),
    ):
        main()

    mock_save.assert_called_once()


def test_main_add_device_aborted_by_host_check(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Adding a device whose host already exists can be aborted."""
    fake_entry = _make_device_entry()
    with (
        patch("axis.cli.packs.devices.load_devices", return_value={"SN1": fake_entry}),
        patch(
            "axis.cli.packs.devices.register_or_update_device_async",
            new=AsyncMock(
                return_value=CommandResult(
                    status="cancelled", message="Device registration aborted."
                )
            ),
        ),
        patch("builtins.input", side_effect=["1", "1", "e"]),
        pytest.raises(SystemExit),
    ):
        main()
    out = capsys.readouterr().out
    assert "aborted" in out.lower()


# ---------------------------------------------------------------------------
# run_on_selected_device - OSError/ValueError branch
# ---------------------------------------------------------------------------


def test_run_on_selected_device_value_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Returns None and prints message on ValueError."""
    op = AsyncMock(side_effect=ValueError("bad state"))
    with (
        patch("axis.cli.packs.devices.AxisDevice"),
        patch("axis.cli.packs.devices.ClientSession"),
    ):
        result = _asyncio.run(run_on_selected_device(_make_device_entry(), op))
    assert result is None
    out = capsys.readouterr().out
    assert "Failed to connect" in out


# ---------------------------------------------------------------------------
# account_management_async - sub-option delegation
# ---------------------------------------------------------------------------


def test_account_management_async_list_users(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Option '1' delegates to _list_users_async."""
    with (
        patch(
            "axis.cli.packs.accounts._list_users_async", new=AsyncMock()
        ) as mock_list,
        patch("builtins.input", side_effect=["1", "b"]),
    ):
        _asyncio.run(account_management_async("SN1", _make_device_entry()))
    mock_list.assert_awaited_once()


def test_account_management_async_create_user(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Option '2' delegates to _create_or_update_user_async."""
    with (
        patch(
            "axis.cli.packs.accounts._create_or_update_user_async",
            new=AsyncMock(),
        ) as mock_create,
        patch("builtins.input", side_effect=["2", "b"]),
    ):
        _asyncio.run(account_management_async("SN1", _make_device_entry()))
    mock_create.assert_awaited_once()


def test_account_management_async_delete_user(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Option '3' delegates to _delete_user_async."""
    with (
        patch(
            "axis.cli.packs.accounts._delete_user_async", new=AsyncMock()
        ) as mock_del,
        patch("builtins.input", side_effect=["3", "b"]),
    ):
        _asyncio.run(account_management_async("SN1", _make_device_entry()))
    mock_del.assert_awaited_once()


# ---------------------------------------------------------------------------
# _create_or_update_user_async paths
# ---------------------------------------------------------------------------


def test_create_or_update_user_async_invalid_username(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Invalid username aborts the flow immediately."""
    with patch("builtins.input", return_value="bad@user"):
        _asyncio.run(_create_or_update_user_async(_make_device_entry()))
    out = capsys.readouterr().out
    assert "Invalid username" in out


def test_create_or_update_user_async_empty_password(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Empty password aborts the flow."""
    with (
        patch("builtins.input", return_value="validuser"),
        patch("axis.cli.packs.accounts.getpass") as mock_gp,
    ):
        mock_gp.getpass.return_value = ""
        _asyncio.run(_create_or_update_user_async(_make_device_entry()))
    out = capsys.readouterr().out
    assert "Password must be" in out


def test_create_or_update_user_async_privilege_back(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Selecting 'b' at privilege prompt aborts the flow."""
    with (
        patch("builtins.input", side_effect=["validuser", "b"]),
        patch("axis.cli.packs.accounts.getpass") as mock_gp,
    ):
        mock_gp.getpass.return_value = "password1"
        _asyncio.run(_create_or_update_user_async(_make_device_entry()))


# ---------------------------------------------------------------------------
# _delete_user_async confirmed deletion
# ---------------------------------------------------------------------------


def test_delete_user_async_confirmed(capsys: pytest.CaptureFixture[str]) -> None:
    """Confirmed deletion runs list and delete operations on selected device."""
    user = MagicMock()
    user.privileges = SecondaryGroup.VIEWER
    fake_users = {"vieweruser": user}
    with (
        patch(
            "axis.cli.packs.accounts.run_on_selected_device",
            new=AsyncMock(side_effect=[fake_users, None]),
        ) as mock_run,
        patch("builtins.input", side_effect=["vieweruser", "y"]),
    ):
        _asyncio.run(_delete_user_async(_make_device_entry()))
    assert mock_run.await_count == 2


# ---------------------------------------------------------------------------
# _select_privilege helper
# ---------------------------------------------------------------------------


def test_select_privilege_valid(capsys: pytest.CaptureFixture[str]) -> None:
    """Returns correct SecondaryGroup for valid index."""
    with patch("builtins.input", return_value="1"):
        result = _select_privilege()
    assert result == SecondaryGroup.VIEWER


def test_select_privilege_back(capsys: pytest.CaptureFixture[str]) -> None:
    """Returns None when user types 'b'."""
    with patch("builtins.input", return_value="b"):
        result = _select_privilege()
    assert result is None


def test_select_privilege_invalid_number(capsys: pytest.CaptureFixture[str]) -> None:
    """Returns None for out-of-range index."""
    with patch("builtins.input", return_value="99"):
        result = _select_privilege()
    assert result is None


def test_select_privilege_non_numeric(capsys: pytest.CaptureFixture[str]) -> None:
    """Returns None for non-numeric, non-'b' input."""
    with patch("builtins.input", return_value="xyz"):
        result = _select_privilege()
    assert result is None


# ---------------------------------------------------------------------------
# main() - successful add device flow
# ---------------------------------------------------------------------------


def test_main_add_device_success(capsys: pytest.CaptureFixture[str]) -> None:
    """Successfully adding a new device saves it to the registry."""
    with (
        patch("axis.cli.packs.devices.load_devices", return_value={}),
        patch(
            "axis.cli.packs.devices.register_or_update_device_async",
            new=AsyncMock(return_value=CommandResult(status="ok", message="ok")),
        ),
        patch("axis.cli.packs.devices.save_devices") as mock_save,
        patch("builtins.input", side_effect=["1", "1", "e"]),
        pytest.raises(SystemExit),
    ):
        main()
    mock_save.assert_called_once()


def test_main_swallows_ctrl_c(capsys: pytest.CaptureFixture[str]) -> None:
    """Ctrl+C is swallowed and the loop continues until explicit exit."""
    runtime = MagicMock()
    runtime.router = MagicMock()
    runtime.router.run = AsyncMock(side_effect=[KeyboardInterrupt, SystemExit(0)])

    with (
        patch("axis.cli.main.build_cli_runtime", return_value=runtime),
        pytest.raises(SystemExit),
    ):
        main()

    assert runtime.router.run.await_count == 2
    out = capsys.readouterr().out
    assert "Interrupted" in out


def test_main_debug_argument_enables_verbose_mode(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Explicit debug argument enables verbose mode and env toggle."""
    debug_env_value = ""

    async def _capture_debug_and_exit(*_args: object, **_kwargs: object) -> None:
        nonlocal debug_env_value
        debug_env_value = os.environ.get("AXIS_CLI_DEBUG", "")
        raise SystemExit(0)

    runtime = MagicMock()
    runtime.router = MagicMock()
    runtime.router.run = AsyncMock(side_effect=_capture_debug_and_exit)

    with (
        patch.dict(os.environ, {}, clear=True),
        patch("axis.cli.main.logging.basicConfig") as mock_basic_config,
        patch("axis.cli.main.build_cli_runtime", return_value=runtime),
        pytest.raises(SystemExit),
    ):
        main(debug=True)

    assert debug_env_value == "1"
    mock_basic_config.assert_called_once_with(
        format="%(message)s",
        level=logging.DEBUG,
        force=True,
    )

    out = capsys.readouterr().out
    assert "Debug mode enabled" in out


def test_main_debug_env_enables_verbose_mode(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AXIS_CLI_DEBUG environment variable enables verbose mode."""
    runtime = MagicMock()
    runtime.router = MagicMock()
    runtime.router.run = AsyncMock(side_effect=SystemExit(0))

    with (
        patch.dict(os.environ, {"AXIS_CLI_DEBUG": "1"}, clear=True),
        patch("axis.cli.main.logging.basicConfig") as mock_basic_config,
        patch("axis.cli.main.build_cli_runtime", return_value=runtime),
        pytest.raises(SystemExit),
    ):
        main()

    mock_basic_config.assert_called_once_with(
        format="%(message)s",
        level=logging.DEBUG,
        force=True,
    )

    out = capsys.readouterr().out
    assert "Debug mode enabled" in out


def test_main_uses_router_runtime() -> None:
    """Main loop dispatches through router runtime."""
    runtime = MagicMock()
    runtime.router = MagicMock()
    runtime.router.run = AsyncMock(side_effect=SystemExit(0))

    with (
        patch.dict(os.environ, {}, clear=True),
        patch("axis.cli.main.build_cli_runtime", return_value=runtime),
        pytest.raises(SystemExit),
    ):
        main()

    runtime.router.run.assert_awaited_once()


def test_main_router_runtime_swallows_ctrl_c() -> None:
    """Router runtime swallows Ctrl+C and continues until explicit exit."""
    runtime = MagicMock()
    runtime.router = MagicMock()
    runtime.router.run = AsyncMock(side_effect=[KeyboardInterrupt, SystemExit(0)])

    with (
        patch.dict(os.environ, {}, clear=True),
        patch("axis.cli.main.build_cli_runtime", return_value=runtime),
        pytest.raises(SystemExit),
    ):
        main()

    assert runtime.router.run.await_count == 2


def test_main_requires_router_runtime() -> None:
    """Main raises RuntimeError when runtime router is missing."""
    runtime = MagicMock()
    runtime.router = None

    with (
        patch.dict(os.environ, {}, clear=True),
        patch("axis.cli.main.build_cli_runtime", return_value=runtime),
        pytest.raises(RuntimeError, match="Router runtime is unavailable"),
    ):
        main()
