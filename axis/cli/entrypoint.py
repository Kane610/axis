"""Bootstrap the optional canonical Axis CLI without affecting library imports."""

import importlib.metadata
import sys

from packaging.requirements import Requirement


def main() -> None:
    """Run the CLI, reporting missing optional dependencies without a traceback."""
    distribution = importlib.metadata.distribution("axis")
    missing: list[str] = []
    for declared in distribution.requires or []:
        requirement = Requirement(declared)
        marker = requirement.marker
        if (
            marker is None
            or marker.evaluate({"extra": ""})
            or not marker.evaluate({"extra": "cli"})
        ):
            continue
        try:
            installed = importlib.metadata.version(requirement.name)
        except importlib.metadata.PackageNotFoundError:
            missing.append(f"{requirement.name}{requirement.specifier}")
        else:
            if installed not in requirement.specifier:
                missing.append(f"{requirement.name}{requirement.specifier}")
    if missing:
        name = distribution.metadata["Name"]
        python_requirement = distribution.metadata["Requires-Python"]
        print(  # noqa: T201
            f"{name} {distribution.version} CLI dependencies are missing or incompatible: "
            f"{', '.join(missing)}. Install with: "
            f"uv tool install --reinstall '{name}[cli]' (Python {python_requirement}).",
            file=sys.stderr,
        )
        raise SystemExit(1)

    from axis.cli.commands import main as run_cli  # noqa: PLC0415

    run_cli()
