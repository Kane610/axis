"""Test installed library and CLI packages, command help, and Zsh completion outside the checkout."""

# ruff: noqa: INP001

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
from tempfile import TemporaryDirectory
from zipfile import ZipFile


def run(
    args: list[str], cwd: Path, env: dict[str, str]
) -> subprocess.CompletedProcess[str]:
    """Run a validation command and retain its output if it fails."""
    return subprocess.run(  # noqa: S603
        args, cwd=cwd, env=env, text=True, capture_output=True, check=True, timeout=180
    )


def require(condition: bool, message: str) -> None:
    """Fail validation explicitly, including when Python assertions are disabled."""
    if not condition:
        raise RuntimeError(message)


def verify_web_artifacts(sdist: Path, wheel: Path) -> None:
    """Check that the sdist is rebuildable and the wheel ships the browser assets."""
    assets = {"axis/web/static/app.js", "axis/web/static/index.html"}
    sources = {
        "web/package.json",
        "web/pnpm-lock.yaml",
        "web/pnpm-workspace.yaml",
        "web/tsconfig.json",
        "web/src/app.ts",
        "web/tests/fixtures/websocket.json",
    }
    with tarfile.open(sdist) as archive:
        contents = {entry.name.partition("/")[2] for entry in archive}
    require(
        assets | sources <= contents,
        f"Missing web files in source distribution: {sorted((assets | sources) - contents)}",
    )
    require(
        not any(path.startswith("web/node_modules/") for path in contents),
        "Source distribution includes installed frontend dependencies.",
    )
    with ZipFile(wheel) as archive:
        contents = set(archive.namelist())
    require(
        assets <= contents, f"Missing web assets in wheel: {sorted(assets - contents)}"
    )
    require(
        not any(path.startswith("web/") for path in contents),
        "Wheel includes frontend development files.",
    )
    sys.stdout.write(
        "Web packaging passed: frontend sources in sdist, browser assets in wheel.\n"
    )


def verify() -> None:
    """Install a built wheel into temporary environments and test it without personal config."""
    repository = Path(__file__).resolve().parents[1]
    with TemporaryDirectory(prefix="axis-cli-install-") as temporary:
        root = Path(temporary)
        home = root / "home"
        home.mkdir()
        env = {**os.environ, "HOME": str(home), "ZDOTDIR": str(home)}
        env.pop("PYTHONPATH", None)
        run(["uv", "build", "--out-dir", str(root / "dist")], repository, env)
        wheel = next((root / "dist").glob("*.whl"))
        verify_web_artifacts(next((root / "dist").glob("*.tar.gz")), wheel)
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
                application = run(
                    [
                        str(python),
                        "-c",
                        (
                            "import asyncio, importlib.util, json, sys\n"
                            "from dataclasses import asdict\n"
                            "from datetime import datetime\n"
                            "from pathlib import Path\n"
                            "from typing import get_type_hints\n"
                            "from aiohttp import ClientSession\n"
                            "from axis.device import AxisDevice\n"
                            "from axis.models.configuration import Configuration\n"
                            "from axis.application import discovery, operations, storage\n"
                            "from axis.application.records import ConnectionSettings, DeviceRecord, HealthSnapshot\n"
                            "async def probe():\n"
                            " async with ClientSession() as session:\n"
                            "  device = AxisDevice(Configuration(session=session, host='camera.local', username='root', password='test-secret'))\n"
                            "  if device.config.session is not session: raise RuntimeError('Library session ownership changed')\n"
                            " return session.closed\n"
                            "record = DeviceRecord('SERIAL', ConnectionSettings('camera.local', 'root', 'test-secret'))\n"
                            "registry = storage.DeviceRegistry(Path('not-created/config.toml'))\n"
                            "print(json.dumps({"
                            "'origin': operations.__file__,"
                            "'summary': asdict(record.summary()),"
                            "'records': len(registry.load()),"
                            "'closed': asyncio.run(probe()),"
                            "'typed': get_type_hints(HealthSnapshot)['observed_at'] is datetime,"
                            "'payload': operations.normalize_payload({'password':'test-secret','value':1}),"
                            "'ui': [n for n in ('click','prompt_toolkit') if importlib.util.find_spec(n)],"
                            "'presentation': [n for n in sys.modules if n.startswith('axis.cli')]"
                            "}))\n"
                        ),
                    ],
                    root,
                    env,
                )
                report = json.loads(application.stdout)
                require(
                    Path(report["origin"]).is_relative_to(environment),
                    f"Wrong application origin: {report}",
                )
                require(
                    not report["ui"] and not report["presentation"],
                    f"Library/application requires presentation: {report}",
                )
                require(
                    report["closed"]
                    and report["typed"]
                    and report["records"] == 0
                    and report["payload"] == {"value": 1}
                    and report["summary"]["serial"] == "SERIAL"
                    and "test-secret" not in application.stdout
                    and "username" not in report["summary"]
                    and not (root / "not-created").exists(),
                    f"Invalid library/application contract: {report}",
                )
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
                sys.stdout.write(
                    "Library/application passed: no UI dependencies, caller-owned session, safe summaries, offline registry.\n"
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
