"""Exercise the installed launcher and suggested prompt through a real terminal."""

from __future__ import annotations

import os
import select
import shutil
import subprocess
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
        read_until(master, b"Select [e]:")
        os.write(master, b"c\n")
        read_until(master, b"axis[no device]>")
        os.write(master, b"axis devices list --json\r")
        output = read_until(master, b"SERIAL")
        assert b"hidden" not in output
        if b"axis[no device]>" not in output:
            read_until(master, b"axis[no device]>")
        os.write(master, b"/back\r")
        read_until(master, b"Select [e]:")
        os.write(master, b"e\n")
        assert process.wait(timeout=5) == 0
        assert not list(home.iterdir())
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        os.close(master)
