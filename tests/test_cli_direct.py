"""Direct coverage test for axis.cli.main (no subprocess).

Covers argument parsing, configuration validation, and TOML output by calling main_async directly.
"""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
import tomli

from axis.cli import main as cli_main


@pytest.mark.asyncio
async def test_cli_valid_config_direct(tmp_path: Path):
    """Test direct CLI call with valid config."""
    args = SimpleNamespace(
        host="192.0.2.1",
        username="user",
        password="pass",
        output=tmp_path / "config.toml",
    )
    with patch("sys.stdout"):
        code = await cli_main.main_async(args)
    assert code == 0
    assert args.output.exists()
    with args.output.open("rb") as f:
        data = tomli.load(f)
    assert data["host"] == "192.0.2.1"
    assert data["username"] == "user"
    assert data["password"] == "pass"


@pytest.mark.asyncio
async def test_cli_invalid_host_direct(tmp_path: Path):
    """Test direct CLI call with invalid host."""
    args = SimpleNamespace(
        host="bad host",
        username="user",
        password="pass",
        output=tmp_path / "config.toml",
    )
    with patch("sys.stderr"):
        code = await cli_main.main_async(args)
    assert code == 1
    assert not args.output.exists()


@pytest.mark.asyncio
async def test_cli_output_write_error(tmp_path: Path):
    """Test direct CLI call with unwritable output path."""
    args = SimpleNamespace(
        host="192.0.2.1",
        username="user",
        password="pass",
        output=Path("/this/path/does/not/exist/config.toml"),
    )
    with patch("sys.stderr"):
        code = await cli_main.main_async(args)
    assert code == 1
