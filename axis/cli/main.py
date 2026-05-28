"""Axis CLI entry point for configuration validation and TOML export.

This CLI allows users to input minimal configuration parameters (host, username, password),
validates them using the Configuration model, and saves the result to a TOML file.
"""

import asyncio
import getpass
from pathlib import Path
import sys
from types import SimpleNamespace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import types

from aiohttp import ClientSession
import tomli_w

from axis.models.configuration import Configuration


async def main_async(args: types.SimpleNamespace) -> int:
    """Run the main async logic for the CLI.

    Args:
        args (argparse.Namespace): Parsed CLI arguments.

    Returns:
        int: Exit code (0 for success, 1 for failure).

    """
    async with ClientSession() as session:
        try:
            config = Configuration(
                session=session,
                host=args.host,
                username=args.username,
                password=args.password,
            )
        except ValueError as exc:
            sys.stderr.write(f"Configuration validation failed: {exc}\n")
            return 1

        toml_dict = config_to_toml_dict(config)
        try:
            with args.output.open("wb") as f:
                tomli_w.dump(toml_dict, f)
        except OSError as exc:
            sys.stderr.write(f"Failed to write TOML file: {exc}\n")
            return 1

        sys.stdout.write(f"Configuration validated and saved to {args.output}\n")
        return 0


"""Axis CLI entry point for configuration validation and TOML export.

This CLI allows users to input minimal configuration parameters (host, username, password),
validates them using the Configuration model, and saves the result to a TOML file.
"""


def prompt_for_config() -> tuple[str, str, str, Path]:
    """Interactively prompt for host, username, password. Output path is always ~/.axis/config.toml."""
    print("Register a new Axis device configuration:\n")  # noqa: T201
    host = input("Device hostname or IP address: ").strip()
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    config_dir = Path.home() / ".axis"
    config_dir.mkdir(parents=True, exist_ok=True)
    output_path = config_dir / "config.toml"
    return host, username, password, output_path


def config_to_toml_dict(config: Configuration) -> dict[str, object]:
    """Convert a Configuration object to a dict suitable for TOML serialization.

    Excludes the session attribute.

    Args:
        config (Configuration): The configuration object.

    Returns:
        dict[str, object]: Dictionary representation for TOML output.

    """
    return {
        "host": config.host,
        "username": config.username,
        "password": config.password,
        "port": config.port,
        "web_proto": str(config.web_proto),
        "verify_ssl": config.verify_ssl,
        "is_companion": config.is_companion,
        "auth_scheme": str(config.auth_scheme),
        "websocket_enabled": config.websocket_enabled,
        "websocket_force": config.websocket_force,
    }


def main() -> None:
    """Run the synchronous entry point for the interactive CLI."""
    host, username, password, output = prompt_for_config()
    args = SimpleNamespace(
        host=host,
        username=username,
        password=password,
        output=output,
    )
    exit_code = asyncio.run(main_async(args))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
