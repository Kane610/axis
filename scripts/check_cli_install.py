"""Verify canonical Axis wheel installation and Zsh startup outside the checkout."""

# ruff: noqa: INP001

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory


def run(
    args: list[str], cwd: Path, env: dict[str, str]
) -> subprocess.CompletedProcess[str]:
    """Run an isolated validation command, preserving full failure evidence."""
    return subprocess.run(  # noqa: S603
        args, cwd=cwd, env=env, text=True, capture_output=True, check=True, timeout=180
    )


def require(condition: bool, message: str) -> None:
    """Fail validation explicitly, including when Python assertions are disabled."""
    if not condition:
        raise RuntimeError(message)


def verify() -> None:
    """Build and exercise base and CLI-extra installations without personal state."""
    repository = Path(__file__).resolve().parents[1]
    with TemporaryDirectory(prefix="axis-cli-install-") as temporary:
        root = Path(temporary)
        home = root / "home"
        home.mkdir()
        env = {**os.environ, "HOME": str(home), "ZDOTDIR": str(home)}
        env.pop("PYTHONPATH", None)
        run(["uv", "build", "--out-dir", str(root / "dist")], repository, env)
        wheel = next((root / "dist").glob("*.whl"))
        for profile in ("base", "cli"):
            environment = root / profile
            run(["uv", "venv", "--python", sys.executable, str(environment)], root, env)
            python = environment / (
                "Scripts/python.exe" if os.name == "nt" else "bin/python"
            )
            package = f"{wheel}[cli]" if profile == "cli" else str(wheel)
            run(["uv", "pip", "install", "--python", str(python), package], root, env)
            probe = run(
                [
                    str(python),
                    "-c",
                    (
                        "import axis, importlib.metadata, json; "
                        "d=importlib.metadata.distribution('axis'); "
                        "print(json.dumps({'origin':axis.__file__,"
                        "'scripts':[e.name for e in d.entry_points if e.group=='console_scripts']}))"
                    ),
                ],
                root,
                env,
            )
            metadata = json.loads(probe.stdout)
            require(
                Path(metadata["origin"]).is_relative_to(environment),
                f"Wrong package origin: {metadata}",
            )
            require(
                metadata["scripts"] == ["axis"],
                f"Wrong executable inventory: {metadata}",
            )
            executable = python.parent / ("axis.exe" if os.name == "nt" else "axis")
            if profile == "base":
                missing = subprocess.run(  # noqa: S603
                    [str(executable), "--help"],
                    cwd=root,
                    env=env,
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=15,
                )
                require(
                    missing.returncode == 1
                    and "axis[cli]" in missing.stderr
                    and "Traceback" not in missing.stderr,
                    f"Invalid library-only CLI bootstrap: {missing}",
                )
                continue
            tree = run(
                [
                    str(python),
                    "-c",
                    (
                        "import click,json; from axis.cli.commands import cli\n"
                        "def paths(c,p):\n"
                        " yield p\n"
                        " if isinstance(c,click.Group):\n"
                        "  for n,s in c.commands.items(): yield from paths(s,p+[n])\n"
                        "print(json.dumps(list(paths(cli,[]))))"
                    ),
                ],
                root,
                env,
            )
            paths = json.loads(tree.stdout)
            for path in paths:
                help_result = run([str(executable), *path, "--help"], root, env)
                require("Usage:" in help_result.stdout, f"Missing help for {path}")
            run([str(python), "-m", "axis", "--help"], root, env)
            nonterminal = subprocess.run(  # noqa: S603
                [str(executable)],
                cwd=root,
                env=env,
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
            )
            require(
                nonterminal.returncode == 2 and "terminal" in nonterminal.stderr,
                f"Invalid non-TTY behavior: {nonterminal}",
            )
            source = root / "axis.zsh"
            source.write_text(
                run([str(executable), "completion", "zsh"], root, env).stdout
            )
            zsh = shutil.which("zsh")
            if zsh is None:
                message = "Zsh is required for the installed CLI check."
                raise RuntimeError(message)
            shell_env = {**env, "PATH": f"{python.parent}{os.pathsep}{env['PATH']}"}
            home_before = set(home.rglob("*"))
            completion = run(
                [
                    zsh,
                    "-f",
                    "-c",
                    (
                        'autoload -Uz compinit; compinit -D; source "$1"; '
                        'test "$_comps[axis]" = _axis_completion; '
                        'COMP_WORDS="axis api li" COMP_CWORD=2 _AXIS_COMPLETE=zsh_complete axis'
                    ),
                    "axis-test",
                    str(source),
                ],
                root,
                shell_env,
            )
            require(
                "list" in completion.stdout.splitlines(),
                f"Invalid installed completion: {completion}",
            )
            require(
                set(home.rglob("*")) == home_before,
                "Shell validation changed the isolated home.",
            )
            sys.stdout.write(
                f"Installed CLI passed: {len(paths)} help paths, canonical entrypoint, Zsh completion.\n"
            )


if __name__ == "__main__":
    try:
        verify()
    except subprocess.CalledProcessError as error:
        sys.stderr.write(error.stdout or "")
        sys.stderr.write(error.stderr or "")
        raise
