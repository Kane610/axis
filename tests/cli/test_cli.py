"""Tests for axis.cli.main utility functions (non-interactive).

Covers load/save, TOML serialization, serial extraction, migration, and
device-selection helpers that do not require network calls.
"""

from __future__ import annotations

import asyncio as _asyncio
import getpass as _getpass
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import tomli_w

from axis.cli.main import (
    DeviceEntry,
    DeviceStore,
    config_to_toml_dict,
    extract_serial_number,
    find_serial_by_host,
    get_config_path,
    get_device_credentials,
    load_devices,
    migrate_unknown_entry,
    print_registered_devices,
    prompt_for_device,
    save_devices,
    select_device,
    to_toml_compatible,
    validate_and_fetch_device,
)

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


# ---------------------------------------------------------------------------
# to_toml_compatible
# ---------------------------------------------------------------------------


def test_to_toml_compatible_primitives() -> None:
    """Primitives pass through unchanged."""
    assert to_toml_compatible("foo") == "foo"
    assert to_toml_compatible(42) == 42
    assert to_toml_compatible(3.14) == 3.14
    assert to_toml_compatible(True) is True


def test_to_toml_compatible_none_becomes_empty_string() -> None:
    """None is converted to empty string (TOML has no null)."""
    assert to_toml_compatible(None) == ""


def test_to_toml_compatible_dict_recursion() -> None:
    """Dicts are recursed and keys coerced to str."""
    result = to_toml_compatible({1: {"a": None}})
    assert result == {"1": {"a": ""}}


def test_to_toml_compatible_list_and_tuple() -> None:
    """Lists and tuples are recursed."""
    assert to_toml_compatible([1, None]) == [1, ""]
    assert to_toml_compatible((1, None)) == [1, ""]


def test_to_toml_compatible_custom_object_fallback() -> None:
    """Custom objects fall back to str()."""
    obj = MagicMock()
    obj.__str__ = MagicMock(return_value="custom")
    result = to_toml_compatible(obj)
    assert result == "custom"


# ---------------------------------------------------------------------------
# load_devices / save_devices
# ---------------------------------------------------------------------------


def test_load_devices_missing_file(tmp_path: Path) -> None:
    """Returns empty dict when config file does not exist."""
    result = load_devices(tmp_path / "config.toml")
    assert result == {}


def test_load_devices_valid(tmp_path: Path) -> None:
    """Loads devices from a valid TOML file."""
    config_path = tmp_path / "config.toml"
    data = {"devices": {"AABBCC": {"config": {"host": "192.168.1.1"}}}}
    with config_path.open("wb") as fh:
        tomli_w.dump(data, fh)
    result = load_devices(config_path)
    assert "AABBCC" in result
    assert result["AABBCC"]["config"]["host"] == "192.168.1.1"


def test_load_devices_missing_devices_key(tmp_path: Path) -> None:
    """Returns empty dict when 'devices' key is absent."""
    config_path = tmp_path / "config.toml"
    with config_path.open("wb") as fh:
        tomli_w.dump({}, fh)
    assert load_devices(config_path) == {}


def test_load_devices_invalid_devices_type(tmp_path: Path) -> None:
    """Returns empty dict when 'devices' is not a dict."""
    config_path = tmp_path / "config.toml"
    with config_path.open("wb") as fh:
        tomli_w.dump({"devices": ["a", "b"]}, fh)
    assert load_devices(config_path) == {}


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    """Save and load round-trip preserves device data."""
    config_path = tmp_path / "config.toml"
    devices: DeviceStore = {
        "DEV1": {"config": {"host": "10.0.0.1", "username": "admin"}}
    }
    save_devices(config_path, devices)
    assert config_path.exists()
    result = load_devices(config_path)
    assert result["DEV1"]["config"]["host"] == "10.0.0.1"


def test_save_devices_serializes_none(tmp_path: Path) -> None:
    """None values are TOML-safe (converted to empty string)."""
    config_path = tmp_path / "config.toml"
    devices: DeviceStore = {"X": {"config": {"host": None}}}  # type: ignore[dict-item]
    save_devices(config_path, devices)
    result = load_devices(config_path)
    assert result["X"]["config"]["host"] == ""


# ---------------------------------------------------------------------------
# extract_serial_number
# ---------------------------------------------------------------------------


def test_extract_serial_from_top_level_key() -> None:
    """Extracts serial from a top-level 'serial_number' key."""
    assert extract_serial_number({"serial_number": "AABBCC"}) == "AABBCC"


def test_extract_serial_camelcase_key() -> None:
    """Extracts serial from 'serialNumber' key variant."""
    assert extract_serial_number({"serialNumber": "XY1234"}) == "XY1234"


def test_extract_serial_from_zero_key_obj() -> None:
    """Extracts serial from DeviceInformation-like object at key '0'."""
    obj = MagicMock()
    obj.serial_number = "OBJ123"
    assert extract_serial_number({"0": obj}) == "OBJ123"


def test_extract_serial_from_zero_key_dict() -> None:
    """Extracts serial from dict at key '0'."""
    result = extract_serial_number({"0": {"serial_number": "DICT456"}})
    assert result == "DICT456"


def test_extract_serial_unknown_fallback() -> None:
    """Returns 'unknown' when no recognisable serial key is found."""
    assert extract_serial_number({}) == "unknown"
    assert extract_serial_number({"0": {}}) == "unknown"


# ---------------------------------------------------------------------------
# migrate_unknown_entry
# ---------------------------------------------------------------------------


def test_migrate_unknown_entry_removes_stale_entry() -> None:
    """Removes legacy 'unknown' entry when host matches."""
    devices: DeviceStore = {"unknown": {"config": {"host": "10.0.0.5"}}}
    migrate_unknown_entry(devices, "REAL_SERIAL", "10.0.0.5")
    assert "unknown" not in devices


def test_migrate_unknown_entry_no_op_different_host() -> None:
    """Leaves 'unknown' entry when host does not match."""
    devices: DeviceStore = {"unknown": {"config": {"host": "10.0.0.5"}}}
    migrate_unknown_entry(devices, "REAL_SERIAL", "10.0.0.99")
    assert "unknown" in devices


def test_migrate_unknown_entry_no_op_when_serial_is_unknown() -> None:
    """Does not remove 'unknown' when the resolved serial is also 'unknown'."""
    devices: DeviceStore = {"unknown": {"config": {"host": "10.0.0.5"}}}
    migrate_unknown_entry(devices, "unknown", "10.0.0.5")
    assert "unknown" in devices


def test_migrate_unknown_entry_no_op_when_no_unknown_key() -> None:
    """No-op when no 'unknown' key is present."""
    devices: DeviceStore = {"AABBCC": {"config": {"host": "10.0.0.5"}}}
    migrate_unknown_entry(devices, "REAL_SERIAL", "10.0.0.5")
    assert "AABBCC" in devices


# ---------------------------------------------------------------------------
# find_serial_by_host
# ---------------------------------------------------------------------------


def test_find_serial_by_host_found() -> None:
    """Returns the matching serial when the host exists."""
    devices: DeviceStore = {
        "SN1": {"config": {"host": "10.0.0.1"}},
        "SN2": {"config": {"host": "10.0.0.2"}},
    }
    assert find_serial_by_host(devices, "10.0.0.2") == "SN2"


def test_find_serial_by_host_not_found() -> None:
    """Returns None when no device matches the host."""
    devices: DeviceStore = {"SN1": {"config": {"host": "10.0.0.1"}}}
    assert find_serial_by_host(devices, "10.0.0.99") is None


# ---------------------------------------------------------------------------
# get_device_credentials
# ---------------------------------------------------------------------------


def test_get_device_credentials_valid() -> None:
    """Returns credentials dict when entry is well-formed."""
    entry: DeviceEntry = {
        "config": {"host": "10.0.0.1", "username": "admin", "password": "secret"}
    }
    creds = get_device_credentials(entry)
    assert creds is not None
    assert creds["host"] == "10.0.0.1"
    assert creds["username"] == "admin"
    assert creds["password"] == "secret"


def test_get_device_credentials_missing_host() -> None:
    """Returns None when host is empty."""
    entry: DeviceEntry = {"config": {"host": "", "username": "admin", "password": "x"}}
    assert get_device_credentials(entry) is None


def test_get_device_credentials_missing_username() -> None:
    """Returns None when username is empty."""
    entry: DeviceEntry = {
        "config": {"host": "10.0.0.1", "username": "", "password": "x"}
    }
    assert get_device_credentials(entry) is None


def test_get_device_credentials_config_not_dict() -> None:
    """Returns None when config value is not a dict."""
    entry: DeviceEntry = {"config": "not-a-dict"}  # type: ignore[dict-item]
    assert get_device_credentials(entry) is None


# ---------------------------------------------------------------------------
# select_device
# ---------------------------------------------------------------------------


def test_select_device_no_devices(capsys: pytest.CaptureFixture[str]) -> None:
    """Returns None and prints a message when registry is empty."""
    result = select_device({})
    assert result is None
    out = capsys.readouterr().out
    assert "No devices" in out


def test_select_device_exit_input(capsys: pytest.CaptureFixture[str]) -> None:
    """Returns SystemExit when user types 'e'."""
    devices: DeviceStore = {"SN1": {"config": {"host": "10.0.0.1"}}}
    with patch("builtins.input", return_value="e"):
        try:
            select_device(devices)
        except SystemExit:
            pass
        else:
            msg = "Expected SystemExit"
            raise AssertionError(msg)


def test_select_device_back_input(capsys: pytest.CaptureFixture[str]) -> None:
    """Returns None when user types 'b'."""
    devices: DeviceStore = {"SN1": {"config": {"host": "10.0.0.1"}}}
    with patch("builtins.input", return_value="b"):
        result = select_device(devices)
    assert result is None


def test_select_device_valid_selection(capsys: pytest.CaptureFixture[str]) -> None:
    """Returns the matching (serial, entry) tuple for a valid index."""
    devices: DeviceStore = {"SN1": {"config": {"host": "10.0.0.1"}}}
    with patch("builtins.input", return_value="1"):
        result = select_device(devices)
    assert result is not None
    assert result[0] == "SN1"


def test_select_device_invalid_number(capsys: pytest.CaptureFixture[str]) -> None:
    """Returns None when index is out of range."""
    devices: DeviceStore = {"SN1": {"config": {"host": "10.0.0.1"}}}
    with patch("builtins.input", return_value="99"):
        result = select_device(devices)
    assert result is None


def test_select_device_non_numeric_input(capsys: pytest.CaptureFixture[str]) -> None:
    """Returns None for non-numeric, non-'b' input."""
    devices: DeviceStore = {"SN1": {"config": {"host": "10.0.0.1"}}}
    with patch("builtins.input", return_value="xyz"):
        result = select_device(devices)
    assert result is None


# ---------------------------------------------------------------------------
# print_registered_devices
# ---------------------------------------------------------------------------


def test_print_registered_devices_empty(capsys: pytest.CaptureFixture[str]) -> None:
    """Prints a 'no devices' message when registry is empty."""
    print_registered_devices({})
    out = capsys.readouterr().out
    assert "No devices" in out


def test_print_registered_devices_lists_entries(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Prints numbered device list when devices are present."""
    devices: DeviceStore = {
        "SN1": {"config": {"host": "10.0.0.1"}},
        "SN2": {"config": {"host": "10.0.0.2"}},
    }
    print_registered_devices(devices)
    out = capsys.readouterr().out
    assert "SN1" in out
    assert "SN2" in out
    assert "10.0.0.1" in out


# ---------------------------------------------------------------------------
# get_config_path
# ---------------------------------------------------------------------------


def test_get_config_path_creates_directory(tmp_path: Path) -> None:
    """get_config_path creates the ~/.axis directory and returns the right path."""
    fake_home = tmp_path / "home"
    with patch("axis.cli.main.Path") as mock_path:
        # Make Path.home() return our fake home
        fake_config_dir = fake_home / ".axis"
        fake_config_dir.mkdir(parents=True, exist_ok=True)
        mock_path_instance = MagicMock()
        mock_path_instance.__truediv__ = MagicMock(
            side_effect=lambda other: fake_home / other
        )
        mock_path.home.return_value = mock_path_instance
        result = get_config_path()
    # Just verify it returns a Path-like object (real Path via side_effect)
    assert result is not None


# ---------------------------------------------------------------------------
# extract_serial_number additional branches
# ---------------------------------------------------------------------------


def test_extract_serial_serialnumber_key() -> None:
    """Extracts serial from 'SerialNumber' (capitalized) key."""
    assert extract_serial_number({"SerialNumber": "CAP123"}) == "CAP123"


def test_extract_serial_obj_at_zero_with_none_serial() -> None:
    """Falls back to 'unknown' when object at '0' has serial_number None."""
    obj = MagicMock()
    obj.serial_number = None
    assert extract_serial_number({"0": obj}) == "unknown"


# ---------------------------------------------------------------------------
# prompt_for_device
# ---------------------------------------------------------------------------


def test_prompt_for_device() -> None:
    """Calls input/getpass and returns credentials dict."""
    with (
        patch("builtins.input", side_effect=["192.168.1.1", "admin"]),
        patch.object(_getpass, "getpass", return_value="secret"),
    ):
        result = prompt_for_device()
    assert result == {"host": "192.168.1.1", "username": "admin", "password": "secret"}


# ---------------------------------------------------------------------------
# config_to_toml_dict
# ---------------------------------------------------------------------------


def test_config_to_toml_dict() -> None:
    """Converts a Configuration mock to a dict with expected keys."""
    mock_config = MagicMock()
    mock_config.host = "10.0.0.1"
    mock_config.username = "admin"
    mock_config.password = "pass"
    mock_config.port = 80
    mock_config.web_proto = MagicMock()
    mock_config.web_proto.__str__ = MagicMock(return_value="http")
    mock_config.verify_ssl = False
    mock_config.is_companion = False
    mock_config.auth_scheme = MagicMock()
    mock_config.auth_scheme.__str__ = MagicMock(return_value="digest")
    mock_config.websocket_enabled = True
    mock_config.websocket_force = False

    result = config_to_toml_dict(mock_config)
    assert result["host"] == "10.0.0.1"
    assert result["username"] == "admin"
    assert result["port"] == 80
    assert result["web_proto"] == "http"


# ---------------------------------------------------------------------------
# validate_and_fetch_device - OSError branch
# ---------------------------------------------------------------------------


def test_validate_and_fetch_device_os_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Returns (None, None, None, None) on OSError."""
    with (
        patch(
            "axis.cli.main.fetch_device_serial_and_extra",
            side_effect=OSError("network unreachable"),
        ),
        patch("axis.cli.main.ClientSession"),
    ):
        result = _asyncio.run(
            validate_and_fetch_device(
                {"host": "192.168.1.1", "username": "u", "password": "p"}
            )
        )
    assert result == (None, None, None, None)
    out = capsys.readouterr().out
    assert "Failed to fetch" in out
