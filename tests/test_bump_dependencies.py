"""Test dependency manifest updates without downloading or installing upgrades."""

import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
from unittest.mock import MagicMock

from packaging.requirements import Requirement
import pytest
import script._maintenance as bump
import tomlkit


@pytest.mark.parametrize(
    ("original", "expected"),
    [
        ("example==1.0", "example==3.2.1"),
        ("example>1.0", "example>=3.2.1"),
        ("example>=1,<2", "example>=3.2.1,<4"),
        (
            'example[extra]>=1; sys_platform == "win32"',
            'example[extra]>=3.2.1; sys_platform == "win32"',
        ),
    ],
)
def test_update_requirement(original: str, expected: str) -> None:
    """Preserve pins, extras, and markers while advancing version bounds."""
    assert bump.updated_requirement(Requirement(original), "3.2.1") == expected


def test_unsupported_constraint() -> None:
    """Reject constraints that cannot be rewritten safely."""
    with pytest.raises(ValueError, match="Unsupported version constraint"):
        bump.updated_requirement(Requirement("example!=1.0"), "3.2.1")


@pytest.fixture
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Provide an isolated project with duplicate requirements across groups."""
    monkeypatch.setattr(bump, "ROOT", tmp_path)
    monkeypatch.setattr(bump.shutil, "which", lambda name: f"/bin/{name}")
    (tmp_path / "web").mkdir()
    (tmp_path / "web/package.json").write_text(
        '{"packageManager":"pnpm@12.21.0","dependencies":{"lit":"^1.0.0"},'
        '"devDependencies":{"vitest":"1.0.0"}}',
    )
    (tmp_path / "pyproject.toml").write_text(
        "# Keep this comment.\n"
        '[build-system]\nrequires = ["wheel==0.1"]\n'
        '[project]\nname = "example"\nrequires-python = ">=3.14.0"\n'
        'dependencies = ["example>1.0"]\n'
        "[project.optional-dependencies]\n"
        'cli = ["example>=1,<2"]\ntest = ["example==1.0"]\n'
        "[dependency-groups]\n"
        'dev = ["example>=1.0", {include-group = "lint"}]\n'
        "lint = []\n",
    )
    return tmp_path


@pytest.mark.parametrize(
    "launcher",
    [
        ["pnpm"],
        ["npm", "exec", "--yes", "--package=pnpm@12.21.0", "--", "pnpm"],
    ],
)
def test_bump_both_ecosystems(
    launcher: list[str],
    project: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Update all Python groups before locking and select only frontend dependencies."""
    if launcher[0] == "npm":
        monkeypatch.setattr(
            bump.shutil,
            "which",
            lambda name: None if name == "pnpm" else f"/bin/{name}",
        )

    def run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        if args[1:3] == ["pip", "compile"]:
            assert kwargs["cwd"] == project
            assert Path(args[3]).read_text() == "example\nwheel\n"
            assert args[args.index("--python-version") + 1] == "3.14.0"
            assert args[args.index("--prerelease") + 1] == "disallow"
            Path(args[args.index("--output-file") + 1]).write_text(
                "# Resolved versions.\n\nexample==3.2.1\nwheel==1.0.0\n",
            )
        return subprocess.CompletedProcess(args, 0, stdout="12.21.0\n")

    runner = MagicMock(side_effect=run)
    monkeypatch.setattr(bump.subprocess, "run", runner)
    bump.main()
    text = (project / "pyproject.toml").read_text()
    document = tomlkit.parse(text)
    assert text.startswith("# Keep this comment.")
    assert document["project"]["requires-python"] == ">=3.14.0"
    assert document["build-system"]["requires"] == ["wheel==1.0.0"]
    assert document["project"]["dependencies"] == ["example>=3.2.1"]
    assert document["project"]["optional-dependencies"] == {
        "cli": ["example>=3.2.1,<4"],
        "test": ["example==3.2.1"],
    }
    assert document["dependency-groups"]["dev"] == [
        "example>=3.2.1",
        {"include-group": "lint"},
    ]
    commands = [
        [Path(call.args[0][0]).name, *call.args[0][1:]]
        for call in runner.call_args_list
    ]
    assert commands[2:] == [
        ["uv", "lock", "--upgrade"],
        ["uv", "sync", "--locked", "--all-extras"],
        [
            *launcher,
            "update",
            "--latest",
            "--lockfile-only",
            "--peer",
            "lit",
            "vitest",
        ],
        [*launcher, "install", "--frozen-lockfile"],
        [*launcher, "build"],
    ]
    assert all(
        call.kwargs["cwd"] == project / "web" for call in runner.call_args_list[4:]
    )


def test_wrong_pnpm_changes_nothing(
    project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Reject the wrong package-manager version before changing Python dependencies."""
    before = (project / "pyproject.toml").read_text()
    runner = MagicMock(return_value=subprocess.CompletedProcess([], 0, stdout="1.0.0"))
    monkeypatch.setattr(bump.subprocess, "run", runner)
    with pytest.raises(SystemExit, match=r"Expected pnpm 12\.21\.0"):
        bump.main()
    assert (project / "pyproject.toml").read_text() == before
    runner.assert_called_once()


def test_resolution_failure_changes_nothing(
    project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Stop on resolver failure instead of writing partial Python version updates."""
    before = (project / "pyproject.toml").read_text()
    runner = MagicMock(
        side_effect=[
            subprocess.CompletedProcess([], 0, stdout="12.21.0"),
            subprocess.CalledProcessError(1, ["uv", "pip", "compile"]),
        ]
    )
    monkeypatch.setattr(bump.subprocess, "run", runner)
    with pytest.raises(subprocess.CalledProcessError):
        bump.main()
    assert (project / "pyproject.toml").read_text() == before
    assert runner.call_count == 2


def test_cli_requires_uv(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail the real script entrypoint explicitly when uv is unavailable."""
    monkeypatch.setattr(bump.shutil, "which", lambda _: None)
    monkeypatch.setattr(sys, "argv", [bump.__file__])
    with pytest.raises(SystemExit, match="uv is required"):
        runpy.run_path(bump.__file__, run_name="__main__")


@pytest.mark.parametrize("problem", ["pnpm", "python minimum", "source dependency"])
def test_preflight_changes_nothing(
    problem: str,
    project: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reject unavailable tooling and unsupported requirements before writing."""
    path = project / "pyproject.toml"
    if problem == "pnpm":
        monkeypatch.setattr(
            bump.shutil, "which", lambda name: "/bin/uv" if name == "uv" else None
        )
        message = "Install Node.js"
    elif problem == "python minimum":
        path.write_text(path.read_text().replace('">=3.14.0"', '"==3.14.0"'))
        message = "Expected one"
    else:
        path.write_text(
            path.read_text().replace(
                '"example>1.0"', '"example @ https://example.invalid/package.whl"'
            )
        )
        message = "Source/URL dependencies"
    before = path.read_text()
    monkeypatch.setattr(
        bump.subprocess,
        "run",
        MagicMock(
            return_value=subprocess.CompletedProcess([], 0, stdout="12.21.0"),
        ),
    )
    with pytest.raises(SystemExit, match=message):
        bump.main()
    assert path.read_text() == before


def test_prerelease_is_not_written(
    project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Do not write a manifest if the resolver returns a prerelease."""
    before = (project / "pyproject.toml").read_text()

    def run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        if args[1:3] == ["pip", "compile"]:
            Path(args[args.index("--output-file") + 1]).write_text(
                "example==3.2.1rc1\n"
            )
        return subprocess.CompletedProcess(args, 0, stdout="12.21.0")

    monkeypatch.setattr(bump.subprocess, "run", run)
    with pytest.raises(ValueError, match="Expected a stable exact version"):
        bump.main()
    assert (project / "pyproject.toml").read_text() == before


@pytest.fixture
def pr_runner(project: Path, monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Simulate Git and GitHub while running the complete updater in isolation."""
    root = Path(bump.__file__).parent.parent
    (project / ".github").mkdir()
    (project / ".github/pull_request_template.md").write_text(
        (root / ".github/pull_request_template.md").read_text()
    )
    (project / "script").mkdir()
    (project / "script/check.sh").write_text((root / "script/check.sh").read_text())
    branch = "master"

    def run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        nonlocal branch
        stdout = ""
        if args[-1] == "--version":
            stdout = "12.21.0"
        elif args[1:3] == ["pip", "compile"]:
            Path(args[args.index("--output-file") + 1]).write_text(
                "example==3.2.1\nwheel==1.0.0\n"
            )
        elif args[:3] == ["gh", "repo", "view"]:
            stdout = (
                '{"nameWithOwner":"Kane610/axis","defaultBranchRef":{"name":"master"}}'
            )
        elif args == ["git", "branch", "--show-current"]:
            stdout = branch
        elif args[:3] == ["git", "switch", "-c"]:
            branch = args[3]
        elif args[:2] == ["git", "rev-parse"]:
            stdout = "same-commit"
        elif args[:3] == ["git", "diff", "--name-only"]:
            stdout = (
                "pyproject.toml\nuv.lock\nweb/package.json\naxis/web/static/app.js\n"
            )
        return subprocess.CompletedProcess(args, 0, stdout=stdout)

    runner = MagicMock(side_effect=run)
    runner.real_run = subprocess.run
    monkeypatch.setattr(bump.subprocess, "run", runner)
    return runner


@pytest.mark.parametrize("launcher", ["pnpm", "npm"])
def test_pr_workflow(
    launcher: str, project: Path, pr_runner: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Publish only checked dependency files with the template and explicit branches."""
    if launcher == "npm":
        monkeypatch.setattr(
            bump.shutil,
            "which",
            lambda name: None if name == "pnpm" else f"/bin/{name}",
        )
        binary = project / "bin"
        binary.mkdir()
        npm = binary / "npm"
        npm.write_text("#!/bin/sh\nprintf '%s\\n' \"$@\"\n")
        npm.chmod(0o755)
    original_run = pr_runner.side_effect
    body = ""

    def run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        nonlocal body
        if args == ["/bin/sh", "script/check.sh"]:
            assert kwargs["cwd"] == project
            env = kwargs["env"]
            if launcher == "npm":
                wrapper = Path(env["PATH"].split(":")[0]) / "pnpm"
                assert wrapper.is_file()
                assert wrapper.stat().st_mode & 0o111
                result = pr_runner.real_run(
                    [str(wrapper), "--version"],
                    env={**env, "PATH": f"{project / 'bin'}:{env['PATH']}"},
                    text=True,
                    stdout=subprocess.PIPE,
                    check=True,
                )
                assert result.stdout.splitlines() == [
                    "exec",
                    "--yes",
                    "--package=pnpm@12.21.0",
                    "--",
                    "pnpm",
                    "--version",
                ]
            assert tomlkit.parse((project / "pyproject.toml").read_text())["project"][
                "dependencies"
            ] == ["example>=3.2.1"]
        elif args[:3] == ["gh", "pr", "create"]:
            body = Path(args[args.index("--body-file") + 1]).read_text()
        return original_run(args, **kwargs)

    pr_runner.side_effect = run
    bump.main(create_pr=True)
    commands = [call.args[0] for call in pr_runner.call_args_list]
    branch = next(
        command[3] for command in commands if command[:3] == ["git", "switch", "-c"]
    )
    assert branch.startswith("dependencies/bump-")
    assert commands.index(["git", "switch", "-c", branch]) < next(
        index
        for index, command in enumerate(commands)
        if command[1:3] == ["pip", "compile"]
    )
    check_index = commands.index(["/bin/sh", "script/check.sh"])
    add_index = commands.index(
        [
            "git",
            "add",
            "--",
            "axis/web/static/app.js",
            "pyproject.toml",
            "uv.lock",
            "web/package.json",
        ]
    )
    assert check_index < add_index
    assert commands[add_index + 1] == [
        "git",
        "commit",
        "-m",
        "Bump Python and frontend dependencies",
        "-m",
        "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>",
    ]
    assert commands[-2] == ["git", "push", "--set-upstream", "origin", branch]
    assert commands[-1][1:9] == [
        "pr",
        "create",
        "--repo",
        "Kane610/axis",
        "--base",
        "master",
        "--head",
        branch,
    ]
    template = (project / ".github/pull_request_template.md").read_text()
    assert [line for line in body.splitlines() if line.startswith("## ")] == [
        line for line in template.splitlines() if line.startswith("## ")
    ]
    assert bump.SUMMARY_PLACEHOLDER not in body
    assert bump.NOTES_PLACEHOLDER not in body
    assert "[issue number]" not in body
    assert "- [ ] New tests added" in body
    assert "- [x] `uv run mypy axis` passes" in body
    for line in (project / "script/check.sh").read_text().splitlines():
        if line.startswith(("uv ", "pnpm ")):
            assert f"`{line}` - passed." in body
    assert not Path(commands[-1][-1]).exists()


@pytest.mark.parametrize(
    ("command", "output", "message"),
    [
        (["git", "status", "--porcelain"], " M README.md", "clean worktree"),
        (
            ["git", "branch", "--show-current"],
            "feature/unrelated",
            "Run --pr from master",
        ),
        (["git", "rev-parse", "HEAD"], "older-commit", "Update your local master"),
    ],
)
def test_pr_preflight_rejects_unsafe_checkout(
    command: list[str],
    output: str,
    message: str,
    project: Path,
    pr_runner: MagicMock,
) -> None:
    """Do not upgrade dependencies from dirty, unrelated, or outdated checkouts."""
    before = (project / "pyproject.toml").read_text()
    original_run = pr_runner.side_effect

    def run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        if args == command:
            return subprocess.CompletedProcess(args, 0, stdout=output)
        return original_run(args, **kwargs)

    pr_runner.side_effect = run
    with pytest.raises(SystemExit, match=message):
        bump.main(create_pr=True)
    assert (project / "pyproject.toml").read_text() == before
    assert not any(
        call.args[0][1:3] in (["switch", "-c"], ["pip", "compile"])
        for call in pr_runner.call_args_list
    )


@pytest.mark.parametrize(
    "problem", ["gh", "template", "changed template", "authentication"]
)
def test_pr_preflight_requires_tooling_and_template(
    problem: str, project: Path, pr_runner: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Fail before mutation when authentication or the supported PR template is unavailable."""
    if problem == "gh":
        monkeypatch.setattr(
            bump.shutil, "which", lambda name: None if name == "gh" else f"/bin/{name}"
        )
        message = "requires git"
    elif problem == "template":
        (project / ".github/pull_request_template.md").unlink()
        message = "template is missing"
    elif problem == "changed template":
        (project / ".github/pull_request_template.md").write_text("New template")
        message = "template changed"
    else:
        original_run = pr_runner.side_effect

        def run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            if args == ["gh", "auth", "status"]:
                raise subprocess.CalledProcessError(1, args)
            return original_run(args, **kwargs)

        pr_runner.side_effect = run
        message = "returned non-zero exit status"
    error = subprocess.CalledProcessError if problem == "authentication" else SystemExit
    with pytest.raises(error, match=message):
        bump.prepare_pr()
    assert not any(
        call.args[0][:3] == ["git", "switch", "-c"] for call in pr_runner.call_args_list
    )


@pytest.mark.parametrize(
    "problem",
    [
        "no changes",
        "bundle only",
        "unexpected file",
        "untracked file",
        "failed checks",
        "checks modify unrelated file",
        "checks remove changes",
        "branch changed",
        "branch changed after commit",
        "hook changes",
        "commit fails",
    ],
)
def test_pr_publication_gates(
    problem: str, project: Path, pr_runner: MagicMock
) -> None:
    """Stop before publishing if there are no dependency changes or safety checks fail."""
    repository, base, branch, template = bump.prepare_pr()
    pr_runner.reset_mock()
    original_run = pr_runner.side_effect
    checked = False
    committed = False

    def run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        nonlocal checked, committed
        stdout = None
        if args == ["/bin/sh", "script/check.sh"]:
            checked = True
            if problem == "failed checks":
                raise subprocess.CalledProcessError(1, args)
        elif args[:2] == ["git", "commit"]:
            committed = True
            if problem == "commit fails":
                raise subprocess.CalledProcessError(1, args)
        elif args[:3] == ["git", "diff", "--name-only"]:
            if problem == "no changes" or (
                checked and problem == "checks remove changes"
            ):
                stdout = ""
            elif problem == "bundle only":
                stdout = "axis/web/static/app.js"
            elif problem == "unexpected file" or (
                checked and problem == "checks modify unrelated file"
            ):
                stdout = "pyproject.toml\nREADME.md"
        elif (
            args == ["git", "ls-files", "--others", "--exclude-standard"]
            and problem == "untracked file"
        ):
            stdout = "personal-notes.txt"
        elif args == ["git", "branch", "--show-current"] and (
            problem == "branch changed"
            or (committed and problem == "branch changed after commit")
        ):
            stdout = "master"
        elif (
            args == ["git", "status", "--porcelain"]
            and committed
            and problem == "hook changes"
        ):
            stdout = " M uv.lock"
        if stdout is not None:
            return subprocess.CompletedProcess(args, 0, stdout=stdout)
        return original_run(args, **kwargs)

    pr_runner.side_effect = run
    if problem in {"no changes", "bundle only", "checks remove changes"}:
        bump.publish_pr(repository, base, branch, template, ["pnpm"])
    else:
        error = (
            subprocess.CalledProcessError
            if problem in {"failed checks", "commit fails"}
            else SystemExit
        )
        with pytest.raises(error):
            bump.publish_pr(repository, base, branch, template, ["pnpm"])
    commands = [call.args[0] for call in pr_runner.call_args_list]
    assert not any(
        command[:2] == ["git", "push"] or command[:3] == ["gh", "pr", "create"]
        for command in commands
    )
    if problem not in {"hook changes", "commit fails", "branch changed after commit"}:
        assert not any(command[:2] == ["git", "commit"] for command in commands)


def test_default_branch_cannot_be_published() -> None:
    """Never allow a caller to bypass the feature-branch gate."""
    with pytest.raises(SystemExit, match="refusing to commit"):
        bump.require_pr_branch("master", "master")


@pytest.mark.parametrize("mode", ["dependencies", "version"])
def test_cli_pr_flag(
    mode: str, project: Path, pr_runner: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The CLI flag enables PR preflight rather than silently performing a normal bump."""
    if mode == "version":
        path = project / "pyproject.toml"
        document = tomlkit.parse(path.read_text())
        document["project"]["version"] = "75"
        path.write_text(tomlkit.dumps(document))
    script = project / "script/_maintenance.py"
    script.parent.mkdir(exist_ok=True)
    script.write_text(Path(bump.__file__).read_text())
    monkeypatch.setattr(
        sys, "argv", [str(script), "--bump-version" if mode == "version" else "--pr"]
    )
    monkeypatch.setattr(
        bump.shutil, "which", lambda name: None if name == "gh" else f"/bin/{name}"
    )
    before = (project / "pyproject.toml").read_text()
    with pytest.raises(SystemExit, match=r"(?:--pr|bump_version\.sh) requires git"):
        runpy.run_path(str(script), run_name="__main__")
    assert (project / "pyproject.toml").read_text() == before


@pytest.mark.parametrize("mode", ["dependencies", "version"])
def test_pr_persists_only_maintenance_commit(
    mode: str,
    project: Path,
    pr_runner: MagicMock,
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """Exercise real Git branches, staging, and a local push without contacting GitHub."""
    real_run = pr_runner.real_run
    remote = tmp_path_factory.mktemp("dependency-remote") / "origin.git"
    if mode == "version":
        (project / "pyproject.toml").write_text(
            "[build-system]\nrequires = []\n"
            '[project]\nname = "example"\nversion = "75"\nrequires-python = ">=3.14"\n'
            "dependencies = []\n"
        )
        real_run(
            ["uv", "lock", "--offline", "--project", str(project)],
            cwd=project,
            check=True,
        )

    def git(*args: str, cwd: Path = project) -> str:
        return real_run(
            ["git", *args], cwd=cwd, text=True, stdout=subprocess.PIPE, check=True
        ).stdout.strip()

    git("init", "--bare", "--initial-branch=main", str(remote))
    git("init", "--initial-branch=main")
    git("config", "user.name", "Test")
    git("config", "user.email", "test@example.invalid")
    git("add", ".")
    git(
        "commit",
        "-m",
        "Create test fixture",
        "-m",
        "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>",
    )
    git("remote", "add", "origin", str(remote))
    git("push", "--set-upstream", "origin", "main")
    base_commit = git("rev-parse", "HEAD")
    original_run = pr_runner.side_effect
    created: list[list[str]] = []

    def run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        if args[0] == "git":
            return real_run(args, **kwargs)
        if mode == "version" and args[1] in {"version", "lock"}:
            return real_run(["uv", *args[1:], "--offline"], **kwargs)
        if args[:3] == ["gh", "repo", "view"]:
            return subprocess.CompletedProcess(
                args,
                0,
                stdout='{"nameWithOwner":"Kane610/axis","defaultBranchRef":{"name":"main"}}',
            )
        if args[:3] == ["gh", "pr", "create"]:
            created.append(args)
        return original_run(args, **kwargs)

    pr_runner.side_effect = run
    bump.main(create_pr=True, bump_version=mode == "version")
    branch = git("branch", "--show-current")
    if mode == "version":
        assert branch == "release/bump-76"
        document = tomlkit.parse((project / "pyproject.toml").read_text())
        assert document["project"]["version"] == "76"
        locked = tomlkit.parse((project / "uv.lock").read_text())["package"]
        assert [(package["name"], package["version"]) for package in locked] == [
            ("example", "76")
        ]
    else:
        assert branch.startswith("dependencies/bump-")
    assert git("status", "--porcelain") == ""
    assert git("rev-parse", "main") == base_commit
    assert git("diff", "--name-only", "main", "HEAD") == (
        "pyproject.toml\nuv.lock" if mode == "version" else "pyproject.toml"
    )
    assert git("rev-parse", "HEAD") == git(
        "--git-dir", str(remote), "rev-parse", f"refs/heads/{branch}"
    )
    assert (
        "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
        in git("log", "-1", "--format=%B")
    )
    assert len(created) == 1
    assert created[0][created[0].index("--base") + 1] == "main"


@pytest.mark.parametrize(
    ("entrypoint_name", "prefix"),
    [("bump_dependencies.sh", []), ("bump_version.sh", ["--bump-version"])],
)
@pytest.mark.parametrize(
    ("arguments", "exit_code"),
    [([], 0), (["--pr", "--help"], 0), (["--pr"], 7)],
)
def test_shell_entrypoint_forwards_arguments(
    entrypoint_name: str,
    prefix: list[str],
    arguments: list[str],
    exit_code: int,
    tmp_path: Path,
) -> None:
    """Run from outside the checkout, preserving arguments and the helper exit status."""
    scripts = tmp_path / "checkout with spaces/script"
    scripts.mkdir(parents=True)
    entrypoint = scripts / entrypoint_name
    entrypoint.write_text(Path(bump.__file__).with_name(entrypoint_name).read_text())
    entrypoint.chmod(0o755)
    binary = tmp_path / "bin"
    binary.mkdir()
    uv = binary / "uv"
    uv.write_text('#!/bin/sh\nprintf \'%s\\n\' "$@" > "$ARGV_FILE"\nexit "$UV_EXIT"\n')
    uv.chmod(0o755)
    argv_file = tmp_path / "arguments"
    result = subprocess.run(  # noqa: S603
        [str(entrypoint), *arguments],
        cwd=tmp_path,
        env={
            **os.environ,
            "PATH": f"{binary}{os.pathsep}{os.environ['PATH']}",
            "ARGV_FILE": str(argv_file),
            "UV_EXIT": str(exit_code),
        },
        check=False,
    )
    assert result.returncode == exit_code
    assert argv_file.read_text().splitlines() == [
        "run",
        "--script",
        str(scripts / "_maintenance.py"),
        *prefix,
        *arguments,
    ]


@pytest.mark.parametrize("entrypoint_name", ["bump_dependencies.sh", "bump_version.sh"])
def test_shell_entrypoint_requires_uv(entrypoint_name: str, tmp_path: Path) -> None:
    """Report missing uv explicitly instead of trying to install it automatically."""
    result = subprocess.run(  # noqa: S603
        ["/bin/bash", str(Path(bump.__file__).with_name(entrypoint_name))],
        cwd=tmp_path,
        env={"PATH": ""},
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "uv is required" in result.stderr


def test_version_pr_updates_dependencies(project: Path, pr_runner: MagicMock) -> None:
    """Include Python and frontend upgrades and the rebuilt bundle in one version PR."""
    path = project / "pyproject.toml"
    original = tomlkit.parse(path.read_text())
    original["project"]["version"] = "75"
    path.write_text(tomlkit.dumps(original))
    frontend_path = project / "web/package.json"
    frontend = json.loads(frontend_path.read_text())
    frontend["version"] = "0.0.0"
    frontend_path.write_text(json.dumps(frontend))
    original_run = pr_runner.side_effect
    body = ""

    def run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        nonlocal body
        if args[1] == "version":
            assert args == [
                "/bin/uv",
                "version",
                "76",
                "--frozen",
                "--project",
                str(project),
            ]
            document = tomlkit.parse(path.read_text())
            assert document["project"]["dependencies"] == ["example>=3.2.1"]
            document["project"]["version"] = args[2]
            path.write_text(tomlkit.dumps(document))
        elif args[:2] == ["pnpm", "update"]:
            updated = json.loads(frontend_path.read_text())
            updated["dependencies"]["lit"] = "^3.3.2"
            updated["devDependencies"]["vitest"] = "5.1.0"
            frontend_path.write_text(json.dumps(updated))
            (project / "web/pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\n")
        elif args == ["pnpm", "build"]:
            bundle = project / "axis/web/static/app.js"
            bundle.parent.mkdir(parents=True)
            bundle.write_text("// Rebuilt frontend.\n")
        elif args[:3] == ["git", "diff", "--name-only"]:
            return subprocess.CompletedProcess(
                args,
                0,
                stdout="pyproject.toml\nuv.lock\nweb/package.json\nweb/pnpm-lock.yaml\naxis/web/static/app.js",
            )
        elif args[:3] == ["gh", "pr", "create"]:
            body = Path(args[args.index("--body-file") + 1]).read_text()
        return original_run(args, **kwargs)

    pr_runner.side_effect = run
    bump.main(bump_version=True)
    document = tomlkit.parse(path.read_text())
    assert document["project"]["version"] == "76"
    assert (
        document["project"]["requires-python"] == original["project"]["requires-python"]
    )
    assert document["project"]["dependencies"] == ["example>=3.2.1"]
    assert document["build-system"]["requires"] == ["wheel==1.0.0"]
    updated = json.loads(frontend_path.read_text())
    assert updated["dependencies"]["lit"] == "^3.3.2"
    assert updated["devDependencies"]["vitest"] == "5.1.0"
    assert updated["version"] == frontend["version"]
    assert updated["packageManager"] == frontend["packageManager"]
    commands = [call.args[0] for call in pr_runner.call_args_list]
    assert ["git", "switch", "-c", "release/bump-76"] in commands
    assert [
        "git",
        "add",
        "--",
        "axis/web/static/app.js",
        "pyproject.toml",
        "uv.lock",
        "web/package.json",
        "web/pnpm-lock.yaml",
    ] in commands
    compile_index = next(
        index
        for index, command in enumerate(commands)
        if command[1:3] == ["pip", "compile"]
    )
    version_index = next(
        index for index, command in enumerate(commands) if command[1] == "version"
    )
    lock_index = commands.index(
        ["/bin/uv", "lock", "--upgrade", "--project", str(project)]
    )
    update_index = commands.index(
        ["pnpm", "update", "--latest", "--lockfile-only", "--peer", "lit", "vitest"]
    )
    build_index = commands.index(["pnpm", "build"])
    check_index = commands.index(["/bin/sh", "script/check.sh"])
    commit_index = next(
        index
        for index, command in enumerate(commands)
        if command[:2] == ["git", "commit"]
    )
    assert (
        compile_index
        < version_index
        < lock_index
        < update_index
        < build_index
        < check_index
        < commit_index
    )
    assert sum(command[:2] == ["git", "commit"] for command in commands) == 1
    assert (
        commands[-1][commands[-1].index("--title") + 1]
        == "Bump version to 76 and update dependencies"
    )
    assert "Version and dependency updates" in body
    assert "update Python and frontend dependencies" in body
    assert "PyPI publication remain separate" in body
    assert "`uv run --locked pytest tests --doctest-modules` - passed." in body


@pytest.mark.parametrize("version", ["75.1", "\u0667\u0665", True, None])
def test_version_format_is_guarded(
    version: str | bool | None, project: Path, pr_runner: MagicMock
) -> None:
    """Reject unsupported release numbering before creating a branch or changing files."""
    path = project / "pyproject.toml"
    document = tomlkit.parse(path.read_text())
    if version is not None:
        document["project"]["version"] = version
    path.write_text(tomlkit.dumps(document))
    before = path.read_text()
    with pytest.raises(SystemExit, match="Expected an integer release version"):
        bump.main(bump_version=True)
    assert path.read_text() == before
    assert not any(
        call.args[0][:3] == ["git", "switch", "-c"] for call in pr_runner.call_args_list
    )


def test_version_write_is_verified(project: Path, pr_runner: MagicMock) -> None:
    """Do not publish when the version command succeeds without writing the requested value."""
    path = project / "pyproject.toml"
    document = tomlkit.parse(path.read_text())
    document["project"]["version"] = "75"
    path.write_text(tomlkit.dumps(document))
    with pytest.raises(SystemExit, match="requested version was not written"):
        bump.main(bump_version=True)
    assert not any(
        call.args[0][:2] in (["git", "commit"], ["git", "push"])
        for call in pr_runner.call_args_list
    )


def test_version_pr_rejects_unrelated_changes(
    project: Path, pr_runner: MagicMock
) -> None:
    """Keep unrelated work out of the combined version and dependency pull request."""
    pr = bump.prepare_pr(version="76")
    original_run = pr_runner.side_effect

    def run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        if args[:3] == ["git", "diff", "--name-only"]:
            return subprocess.CompletedProcess(
                args, 0, stdout="pyproject.toml\nREADME.md"
            )
        return original_run(args, **kwargs)

    pr_runner.side_effect = run
    pr_runner.reset_mock()
    with pytest.raises(SystemExit, match="Unexpected changes"):
        bump.publish_pr(*pr, ["pnpm"], version="76")
    assert not any(
        call.args[0][:2] in (["git", "commit"], ["git", "push"])
        for call in pr_runner.call_args_list
    )


@pytest.mark.parametrize("stage", ["resolution", "frontend update"])
def test_version_dependency_failure_stops_publication(
    stage: str, project: Path, pr_runner: MagicMock
) -> None:
    """Never publish a release PR when either ecosystem's dependency update fails."""
    path = project / "pyproject.toml"
    document = tomlkit.parse(path.read_text())
    document["project"]["version"] = "75"
    path.write_text(tomlkit.dumps(document))
    before = path.read_text()
    original_run = pr_runner.side_effect

    def run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        if (stage == "resolution" and args[1:3] == ["pip", "compile"]) or (
            stage == "frontend update" and args[:2] == ["pnpm", "update"]
        ):
            raise subprocess.CalledProcessError(1, args)
        if args[1] == "version":
            updated = tomlkit.parse(path.read_text())
            updated["project"]["version"] = args[2]
            path.write_text(tomlkit.dumps(updated))
        return original_run(args, **kwargs)

    pr_runner.side_effect = run
    with pytest.raises(subprocess.CalledProcessError):
        bump.main(bump_version=True)
    if stage == "resolution":
        assert path.read_text() == before
    assert not any(
        call.args[0][:2] in (["git", "commit"], ["git", "push"])
        or call.args[0][:3] == ["gh", "pr", "create"]
        for call in pr_runner.call_args_list
    )


def test_check_script_runs_outside_checkout(tmp_path: Path) -> None:
    """Keep validation rooted in the checkout and invoke the relocated packaging check."""
    binary = tmp_path / "bin"
    binary.mkdir()
    for tool in ("uv", "pnpm"):
        executable = binary / tool
        executable.write_text(
            '#!/bin/sh\nprintf \'%s|%s\\n\' "$PWD" "$*" >> "$COMMAND_LOG"\n'
        )
        executable.chmod(0o755)
    log = tmp_path / "commands"
    checker = Path(bump.__file__).with_name("check.sh")
    subprocess.run(  # noqa: S603
        ["/bin/sh", str(checker)],
        cwd=tmp_path,
        env={
            **os.environ,
            "PATH": f"{binary}{os.pathsep}{os.environ['PATH']}",
            "COMMAND_LOG": str(log),
        },
        check=True,
    )
    commands = log.read_text().splitlines()
    repository = checker.parent.parent.resolve()
    assert all(command.startswith(f"{repository}|") for command in commands)
    assert f"{repository}|--dir web test:e2e" in commands
    assert commands[-1] == (
        f"{repository}|run --locked python script/check_cli_install.py"
    )
