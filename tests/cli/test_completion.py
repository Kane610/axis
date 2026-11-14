"""Exercise real Zsh completion protocols with isolated homes and local registries."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess

from click.testing import CliRunner
import pytest

from axis.cli.commands import cli
from axis.cli.storage import ConnectionSettings, DeviceRecord, DeviceRegistry


def test_zsh_protocol_and_registered_function(tmp_path: Path) -> None:
    """Real Zsh source, option/choice completion, aliases, and quoting work offline."""
    zsh = shutil.which("zsh")
    assert zsh is not None, "Install Zsh to verify the supported completion shell."
    executable = Path(__file__).resolve().parents[2] / ".venv" / "bin" / "axis"
    # Use the repository environment's installed entrypoint, not module invocation.
    executable = Path(shutil.which("axis") or executable)
    config = tmp_path / "config with spaces.toml"
    DeviceRegistry(config).upsert(
        DeviceRecord(
            "SERIAL",
            ConnectionSettings("camera", "root", "secret"),
            "front door",
            "Model",
        )
    )
    source = tmp_path / "completion.zsh"
    source.write_text(CliRunner().invoke(cli, ["completion", "zsh"]).stdout)
    home = tmp_path / "home"
    home.mkdir()
    environment = {
        **os.environ,
        "HOME": str(home),
        "ZDOTDIR": str(home),
        "PATH": f"{executable.parent}{os.pathsep}{os.environ['PATH']}",
        "PYTHONPATH": "",
    }
    script = """
autoload -Uz compinit
compinit -D
source "$1"
_describe() { local arrayname=$3; print -rl -- "${(@P)arrayname}"; }
compadd() { local arrayname=${@[-1]}; print -rl -- "${(@P)arrayname}"; }
words=(axis --config "$2" api list --device front)
CURRENT=7
_axis_completion
words=(axis events listen --stream-mode e)
CURRENT=5
_axis_completion
words=(axis api list --d)
CURRENT=4
_axis_completion
"""
    result = subprocess.run(  # noqa: S603
        [zsh, "-f", "-c", script, "axis-test", str(source), str(config)],
        env=environment,
        text=True,
        capture_output=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "front door:" in result.stdout
    assert "event" in result.stdout
    assert "--device" in result.stdout
    assert "secret" not in result.stdout + result.stderr
    assert not list(home.iterdir())


@pytest.mark.parametrize(
    ("words", "index", "expected"),
    [
        ("axis api li", "2", "list"),
        ("axis events listen --stream-mode e", "4", "event"),
        ("axis api list --d", "3", "--device"),
    ],
)
def test_installed_completion_protocol(
    words: str, index: str, expected: str, tmp_path: Path
) -> None:
    """Installed executable honors Click's actual Zsh completion environment."""
    executable = shutil.which("axis")
    assert executable is not None
    result = subprocess.run(  # noqa: S603
        [executable],
        env={
            **os.environ,
            "_AXIS_COMPLETE": "zsh_complete",
            "COMP_WORDS": words,
            "COMP_CWORD": index,
            "HOME": str(tmp_path),
        },
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert expected in result.stdout.splitlines()
