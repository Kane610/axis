"""Test suite for the Axis CLI configuration tool.

Covers argument parsing, configuration validation, and TOML output.
"""

from pathlib import Path
import subprocess

import tomli

CLI_PATH = Path(__file__).parent.parent / "axis" / "cli" / "main.py"


def run_cli(args: list[str], tmp_path: Path) -> tuple[int, Path, str, str]:
    """Run the CLI as a subprocess and return (exit_code, output_file, stdout, stderr)."""
    output_file = tmp_path / "config.toml"
    cmd = [
        "python3",
        str(CLI_PATH),
        "--host",
        "192.0.2.1",
        "--username",
        "user",
        "--password",
        "pass",
        "--output",
        str(output_file),
    ]
    cmd.extend(args)
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)  # noqa: S603
    return proc.returncode, output_file, proc.stdout, proc.stderr


def test_cli_valid_config(tmp_path: Path) -> None:
    """Test CLI with valid minimal configuration."""
    code, output_file, stdout, stderr = run_cli([], tmp_path)
    assert code == 0
    assert output_file.exists()
    with output_file.open("rb") as f:
        data = tomli.load(f)
    assert data["host"] == "192.0.2.1"
    assert data["username"] == "user"
    assert data["password"] == "pass"
    assert data["port"] in (80, 443)
    assert "Configuration validated and saved" in stdout
    assert stderr == ""


def test_cli_invalid_host(tmp_path: Path) -> None:
    """Test CLI with invalid host (should fail validation)."""
    code, output_file, _stdout, stderr = run_cli(["--host", "bad host"], tmp_path)
    assert code == 1
    assert not output_file.exists()
    assert "validation failed" in stderr.lower()


def test_cli_missing_args(tmp_path: Path) -> None:
    """Test CLI with missing required arguments (should fail)."""
    cmd = [
        "python3",
        str(CLI_PATH),
        "--host",
        "192.0.2.1",
        # Missing username and password
        "--output",
        str(tmp_path / "config.toml"),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)  # noqa: S603
    assert proc.returncode != 0
    assert "usage:" in proc.stderr.lower()
