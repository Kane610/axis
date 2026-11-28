# /// script
# requires-python = ">=3.14"
# dependencies = ["packaging", "tomlkit"]
# ///
"""Implement dependency and release version updates for the shell entry points."""

import argparse
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name
from packaging.version import Version
import tomlkit

ROOT = Path(__file__).resolve().parent.parent
PR_FILES = (
    "pyproject.toml",
    "uv.lock",
    "web/package.json",
    "web/pnpm-lock.yaml",
    "axis/web/static/app.js",
)
SUMMARY_PLACEHOLDER = '[One-sentence summary, e.g., "Adds new PTZ handler with PARAM_CGI_FALLBACK support"]'
NOTES_PLACEHOLDER = "[Context for reviewers: what to focus on, known limitations, decisions made, or why this approach was chosen]"


def command_output(*args: str) -> str:
    """Read command output while leaving failures and stderr visible."""
    return subprocess.run(  # noqa: S603
        list(args),
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        check=True,
    ).stdout.strip()


def prepare_pr(*, version: str | None = None) -> tuple[str, str, str, str]:
    """Create a feature branch only from a clean, current default branch."""
    operation = "bump_version.sh" if version else "--pr"
    if not shutil.which("git") or not shutil.which("gh"):
        sys.exit(f"{operation} requires git and the authenticated GitHub CLI (gh).")
    if command_output("git", "status", "--porcelain"):
        sys.exit(
            f"{operation} requires a clean worktree. Commit or set aside your changes first."
        )
    template_path = ROOT / ".github/pull_request_template.md"
    if not template_path.is_file():
        sys.exit("The repository PR template is missing; no changes were made.")
    template = template_path.read_text()
    if SUMMARY_PLACEHOLDER not in template or NOTES_PLACEHOLDER not in template:
        sys.exit("The PR template changed. Update this script before using --pr.")
    command_output("gh", "auth", "status")
    repository = json.loads(
        command_output(
            "gh",
            "repo",
            "view",
            "--json",
            "nameWithOwner,defaultBranchRef",
        )
    )
    base = repository["defaultBranchRef"]["name"]
    if command_output("git", "branch", "--show-current") != base:
        sys.exit(
            f"Run {operation} from {base} so unrelated feature commits are not included."
        )
    command_output("git", "fetch", "origin", base)
    if command_output("git", "rev-parse", "HEAD") != command_output(
        "git", "rev-parse", f"origin/{base}"
    ):
        sys.exit(f"Update your local {base} to origin/{base} before running --pr.")
    branch = (
        f"release/bump-{version}"
        if version
        else f"dependencies/bump-{datetime.now(UTC):%Y%m%d-%H%M%S}"
    )
    sys.stdout.write(
        f"Creating {branch} from {base}; only validated changes will be published.\n"
    )
    command_output("git", "switch", "-c", branch)
    return repository["nameWithOwner"], base, branch, template


def changed_files() -> set[str]:
    """Include tracked and untracked changes so unrelated work cannot be committed."""
    return set(command_output("git", "diff", "--name-only", "HEAD").splitlines()) | set(
        command_output(
            "git", "ls-files", "--others", "--exclude-standard"
        ).splitlines(),
    )


def require_pr_branch(branch: str, base: str) -> None:
    """Refuse to commit or push if the active branch changed or is the default branch."""
    if (
        branch in {"master", base}
        or command_output("git", "branch", "--show-current") != branch
    ):
        sys.exit("The active branch changed; refusing to commit or push.")


def publish_pr(
    repository: str,
    base: str,
    branch: str,
    template: str,
    pnpm: list[str],
    *,
    version: str | None = None,
) -> None:
    """Run the complete repository checks before committing, pushing, and opening a PR."""
    allowed_files = PR_FILES
    required_files = PR_FILES[:4]
    title = (
        f"Bump version to {version} and update dependencies"
        if version
        else "Bump Python and frontend dependencies"
    )
    change = "Version and dependency" if version else "Dependency-only"
    files = changed_files()
    if files - set(allowed_files):
        sys.exit(
            f"Unexpected changes; review them before publishing: {', '.join(sorted(files - set(allowed_files)))}"
        )
    if not files.intersection(required_files):
        sys.stdout.write("No manifest changes; no commit, push, or PR created.\n")
        return
    with TemporaryDirectory(prefix="axis-dependency-pr-") as temporary:
        env = os.environ.copy()
        if pnpm[0] != "pnpm":
            wrapper = Path(temporary) / "pnpm"
            wrapper.write_text(f'#!/bin/sh\nexec {shlex.join(pnpm)} "$@"\n')
            wrapper.chmod(0o755)
            env["PATH"] = f"{temporary}{os.pathsep}{env.get('PATH', '')}"
        subprocess.run(
            ["/bin/sh", "script/check.sh"],
            cwd=ROOT,
            env=env,
            check=True,
        )
        files = changed_files()
        if files - set(allowed_files):
            sys.exit("Checks left unrelated changes. Review them before publishing.")
        if not files.intersection(required_files):
            sys.stdout.write(
                "No manifest changes remain after checks; no PR created.\n"
            )
            return
        require_pr_branch(branch, base)
        sys.stdout.write(
            f"Checks passed. Committing {', '.join(sorted(files))}, pushing {branch}, and opening a PR.\n"
        )
        command_output("git", "add", "--", *sorted(files))
        subprocess.run(  # noqa: S603
            [  # noqa: S607
                "git",
                "commit",
                "-m",
                title,
                "-m",
                "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>",
            ],
            cwd=ROOT,
            check=True,
        )
        if command_output("git", "status", "--porcelain"):
            sys.exit(
                "Commit hooks left changes. Review them before pushing or opening a PR."
            )
        require_pr_branch(branch, base)
        subprocess.run(  # noqa: S603
            ["git", "push", "--set-upstream", "origin", branch],  # noqa: S607
            cwd=ROOT,
            check=True,
        )
        checks = [
            line
            for line in (ROOT / "script/check.sh").read_text().splitlines()
            if line.startswith(("uv ", "pnpm "))
        ]
        evidence = "\n".join(f"- `{command}` - passed." for command in checks)
        body = template.replace(
            SUMMARY_PLACEHOLDER,
            (
                f"Bump the axis release version to {version} and update Python and frontend dependencies to the latest eligible stable releases."
                if version
                else "Bump Python and frontend dependencies to the latest eligible stable releases."
            ),
        )
        body = body.replace("Closes #[issue number] (if applicable)", "None.")
        notes = (
            "Version and dependency updates; review major-version compatibility and the generated frontend bundle. GitHub release creation and PyPI publication remain separate."
            if version
            else "Dependency-only update; review major-version compatibility and the generated frontend bundle."
        )
        body = body.replace(
            NOTES_PLACEHOLDER,
            f"{notes}\n\n`sh script/check.sh` - passed.\n\n{evidence}",
        )
        for item in (
            "`uv run ruff check .` passes",
            "`uv run ruff format --check .` passes",
            "`uv run mypy axis` passes",
            "`uv run pytest` passes (coverage ≥95%)",
            "Commit hooks modified files? If so, re-staged and re-ran checks",
            "No unrelated code/formatting changes",
        ):
            body = body.replace(f"- [ ] {item}", f"- [x] {item}")
        body = body.replace(
            "- [ ] New tests added for new code (100% coverage for new code)",
            f"- [ ] New tests added for new code (100% coverage for new code) - not applicable; {change.lower()} changes.",
        )
        body_path = Path(temporary) / "body.md"
        body_path.write_text(body)
        subprocess.run(  # noqa: S603
            [  # noqa: S607
                "gh",
                "pr",
                "create",
                "--repo",
                repository,
                "--base",
                base,
                "--head",
                branch,
                "--title",
                title,
                "--body-file",
                str(body_path),
            ],
            cwd=ROOT,
            check=True,
        )


def updated_requirement(requirement: Requirement, version: str) -> str:
    """Keep exact pins and advance minimum bounds and existing major caps."""
    name = requirement.name
    if requirement.extras:
        name += f"[{','.join(sorted(requirement.extras))}]"
    operators = {specifier.operator for specifier in requirement.specifier}
    if operators == {"=="}:
        bounds = f"=={version}"
    elif operators <= {">", ">=", "<"}:
        bounds = f">={version}"
        if "<" in operators:
            bounds += f",<{Version(version).major + 1}"
    else:
        msg = f"Unsupported version constraint: {requirement}. Update it manually."
        raise ValueError(msg)
    marker = f"; {requirement.marker}" if requirement.marker else ""
    return f"{name}{bounds}{marker}"


def main(*, create_pr: bool = False, bump_version: bool = False) -> None:
    """Update dependencies and optionally bump the integer release version in the same PR."""
    uv = shutil.which("uv")
    if not uv:
        sys.exit("uv is required. Run ./script/setup.sh first.")
    frontend = ROOT / "web"
    package = json.loads((frontend / "package.json").read_text())
    expected = package["packageManager"].removeprefix("pnpm@").split("+")[0]
    pnpm = (
        ["pnpm"]
        if shutil.which("pnpm")
        else [
            "npm",
            "exec",
            "--yes",
            f"--package=pnpm@{expected}",
            "--",
            "pnpm",
        ]
    )
    if not shutil.which(pnpm[0]):
        sys.exit(
            "Install Node.js with npm, or the pnpm version pinned in web/package.json."
        )
    if pnpm[0] == "npm":
        sys.stdout.write(
            f"pnpm is not on PATH; npm will run the pinned pnpm {expected}.\n"
        )
    actual = subprocess.run(  # noqa: S603
        [*pnpm, "--version"],
        cwd=frontend,
        text=True,
        stdout=subprocess.PIPE,
        check=True,
    ).stdout.strip()
    if actual != expected:
        sys.exit(f"Expected pnpm {expected}, found {actual}. Use the pinned version.")

    path = ROOT / "pyproject.toml"
    document = tomlkit.parse(path.read_text())
    project = document["project"]
    version: str | None = None
    if bump_version:
        current = project.get("version")
        if (
            not isinstance(current, str)
            or not current.isascii()
            or not current.isdecimal()
        ):
            sys.exit("Expected an integer release version; no changes were made.")
        version = str(int(current) + 1)
    floors = [
        specifier.version
        for specifier in SpecifierSet(project["requires-python"])
        if specifier.operator == ">="
    ]
    if len(floors) != 1:
        sys.exit("Expected one >= Python minimum in requires-python.")
    arrays = [
        document["build-system"]["requires"],
        project["dependencies"],
        *project.get("optional-dependencies", {}).values(),
        *document.get("dependency-groups", {}).values(),
    ]
    requirements = [
        Requirement(value)
        for array in arrays
        for value in array
        if isinstance(value, str)
    ]
    if any(requirement.url for requirement in requirements):
        sys.exit(
            "Source/URL dependencies need manual upgrades; no manifests were changed."
        )
    pr = prepare_pr(version=version) if create_pr or bump_version else None
    names = sorted(
        {canonicalize_name(requirement.name) for requirement in requirements}
    )
    with TemporaryDirectory(prefix="axis-dependency-bump-") as temporary:
        source = Path(temporary) / "requirements.in"
        resolved = Path(temporary) / "requirements.txt"
        source.write_text("\n".join(names) + "\n")
        subprocess.run(  # noqa: S603
            [
                uv,
                "pip",
                "compile",
                str(source),
                "--upgrade",
                "--prerelease",
                "disallow",
                "--no-deps",
                "--python-version",
                floors[0],
                "--no-header",
                "--no-annotate",
                "--output-file",
                str(resolved),
            ],
            cwd=ROOT,
            check=True,
        )
        versions = {}
        for line in resolved.read_text().splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            requirement = Requirement(line)
            (specifier,) = requirement.specifier
            if specifier.operator != "==" or Version(specifier.version).is_prerelease:
                msg = f"Expected a stable exact version, found {line}."
                raise ValueError(msg)
            versions[canonicalize_name(requirement.name)] = specifier.version
    replacements = {
        str(requirement): updated_requirement(
            requirement, versions[canonicalize_name(requirement.name)]
        )
        for requirement in requirements
    }
    for array in arrays:
        for index, value in enumerate(array):
            if isinstance(value, str):
                array[index] = replacements[str(Requirement(value))]
    path.write_text(tomlkit.dumps(document))
    if version:
        subprocess.run(  # noqa: S603
            [uv, "version", version, "--frozen", "--project", str(ROOT)],
            cwd=ROOT,
            check=True,
        )
        if tomlkit.parse(path.read_text())["project"].get("version") != version:
            sys.exit("The requested version was not written; refusing to publish.")

    project_options = ["--project", str(ROOT)] if version else []
    subprocess.run(  # noqa: S603
        [uv, "lock", "--upgrade", *project_options], cwd=ROOT, check=True
    )
    subprocess.run(  # noqa: S603
        [uv, "sync", "--locked", "--all-extras", *project_options], cwd=ROOT, check=True
    )
    frontend_names = sorted(
        {
            name
            for group in (
                "dependencies",
                "devDependencies",
                "optionalDependencies",
                "peerDependencies",
            )
            for name in package.get(group, {})
        }
    )
    subprocess.run(  # noqa: S603
        [*pnpm, "update", "--latest", "--lockfile-only", "--peer", *frontend_names],
        cwd=frontend,
        check=True,
    )
    subprocess.run([*pnpm, "install", "--frozen-lockfile"], cwd=frontend, check=True)  # noqa: S603
    subprocess.run([*pnpm, "build"], cwd=frontend, check=True)  # noqa: S603
    if pr:
        publish_pr(*pr, pnpm, version=version)
    else:
        sys.stdout.write(
            "Dependencies updated and frontend rebuilt. Review the diff and run sh script/check.sh before committing.\n"
        )


if __name__ == "__main__":
    version_mode = "--bump-version" in sys.argv[1:]
    parser = argparse.ArgumentParser(
        prog="bump_version.sh" if version_mode else "bump_dependencies.sh",
        description=(
            "Update dependencies, bump the integer release version, and open a validated GitHub PR."
            if version_mode
            else "Update Python and frontend dependencies to stable releases."
        ),
    )
    parser.add_argument(
        "--bump-version",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    if not version_mode:
        parser.add_argument(
            "--pr",
            action="store_true",
            help="Validate dependency updates, commit on a feature branch, and open a GitHub PR.",
        )
    args = parser.parse_args()
    main(create_pr=not version_mode and args.pr, bump_version=args.bump_version)
