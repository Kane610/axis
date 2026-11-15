"""Exercise the installed launcher and suggested prompt through a real terminal."""

from __future__ import annotations

import json
import os
import select
import shutil
import signal
import subprocess
import sys
import time
from typing import TYPE_CHECKING

from axis.cli.storage import ConnectionSettings, DeviceRecord, DeviceRegistry

if TYPE_CHECKING:
    from pathlib import Path


def read_until(descriptor: int, expected: bytes) -> bytes:
    """Read terminal output with a deadline and answer cursor-position requests."""
    output = b""
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        readable, _, _ = select.select([descriptor], [], [], 0.2)
        if not readable:
            continue
        chunk = os.read(descriptor, 65536)
        output += chunk
        if b"\x1b[6n" in chunk:
            os.write(descriptor, b"\x1b[1;1R")
        if expected in output:
            return output
    message = f"Terminal did not produce {expected!r}: {output!r}"
    raise AssertionError(message)


def test_real_terminal_launcher_and_command_prompt(tmp_path: Path) -> None:
    """Guided navigation and pasted direct commands work in an actual PTY."""
    executable = shutil.which("axis")
    assert executable is not None
    config = tmp_path / "devices.toml"
    DeviceRegistry(config).upsert(
        DeviceRecord("SERIAL", ConnectionSettings("camera", "root", "hidden"), "front")
    )
    home = tmp_path / "home"
    home.mkdir()
    master, slave = os.openpty()
    process = subprocess.Popen(  # noqa: S603
        [executable, "--config", str(config)],
        stdin=slave,
        stdout=slave,
        stderr=slave,
        env={**os.environ, "HOME": str(home)},
        start_new_session=True,
    )
    os.close(slave)
    try:
        read_until(master, b"Select:")
        os.write(master, b"c\n")
        read_until(master, b"axis[no device]>")
        os.write(master, b"axis devices list --json\r")
        output = read_until(master, b"SERIAL")
        assert b"hidden" not in output
        if b"axis[no device]>" not in output:
            read_until(master, b"axis[no device]>")
        os.write(master, b"/back\r")
        read_until(master, b"Select:")
        os.write(master, b"\n")
        assert b"Axis / home" in read_until(master, b"Select:")
        os.write(master, b"2\n")
        output = read_until(master, b"Select [b]:")
        assert b"Axis / Manage saved devices" in output
        assert b"without contacting devices." in output
        os.write(master, b"3\n")
        output = read_until(master, b"Hostname or IP, without scheme or path.:")
        assert b"Ctrl-C cancels this command" in output
        os.write(master, b"b\n")
        read_until(master, b"Device login name.:")
        process.send_signal(signal.SIGINT)
        output = read_until(master, b"Select [b]:")
        assert b"Cancelled; returning to the menu." in output
        assert b"Axis / Manage saved devices" in output
        os.write(master, b"\n")
        read_until(master, b"Select:")
        os.write(master, b"1\n")
        read_until(master, b"Ctrl-C cancels) [b]:")
        os.write(master, b"\n")
        assert b"Axis / home" in read_until(master, b"Select:")
        os.write(master, b"1\n")
        output = read_until(master, b"Ctrl-C cancels) [b]:")
        assert b"front (SERIAL, camera)" in output
        os.write(master, b"1\n")
        output = read_until(master, b"Select [b]:")
        assert b"Axis / Use a device" in output
        assert b"Device: SERIAL" in output
        assert b"Health" in output
        assert b"APIs" in output
        os.write(master, b"\n")
        read_until(master, b"Select:")
        os.write(master, b"e\n")
        assert process.wait(timeout=5) == 0
        assert not list(home.iterdir())
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        os.close(master)


def test_discovery_interface_warning_preserves_json(tmp_path: Path) -> None:
    """A real CLI process reports a partial-scan warning while keeping stdout valid JSON."""
    code = """
import errno
import logging
import sys
from unittest.mock import patch
from axis.cli import commands

async def discover_axis_devices(scan_seconds: float = 5.0) -> list[dict[str, str]]:
    try:
        raise OSError(errno.ENETDOWN, "Network is down")
    except OSError:
        logging.getLogger("zeroconf").warning("Error with socket 7", exc_info=True)
    return [{"host": "192.0.2.1", "name": "Axis", "macaddress": "00:40:8c:11:22:33"}]

sys.argv = ["axis", "--config", sys.argv[1], "devices", "discover", "--json"]
with patch.object(commands, "discover_axis_devices", discover_axis_devices):
    commands.main()
"""
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-c", code, str(tmp_path / "devices.toml")],
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(result.stdout) == [
        {"host": "192.0.2.1", "name": "Axis", "macaddress": "00:40:8c:11:22:33"}
    ]
    assert "Warning: a network interface is down" in result.stderr
    assert "discovery results may be incomplete" in result.stderr
    assert "Traceback" not in result.stderr
    assert "OSError" not in result.stderr
