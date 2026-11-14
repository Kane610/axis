"""Bootstrap the optional canonical Axis CLI without affecting library imports."""

import importlib.util
import sys


def main() -> None:
    """Run the CLI, reporting missing optional dependencies without a traceback."""
    missing = [
        name
        for name in ("click", "prompt_toolkit")
        if importlib.util.find_spec(name) is None
    ]
    if missing:
        print(  # noqa: T201
            "Axis CLI dependencies are missing. Install with: "
            "uv tool install 'axis[cli]' (Python 3.14 or newer).",
            file=sys.stderr,
        )
        raise SystemExit(1)

    from axis.cli.commands import main as run_cli  # noqa: PLC0415

    run_cli()
