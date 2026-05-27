"""Axis CLI entry point for configuration validation and TOML export.

This CLI allows users to input minimal configuration parameters (host, username, password),
validates them using the Configuration model, and saves the result to a TOML file.
"""

import argparse
import asyncio
from pathlib import Path
import sys

from aiohttp import ClientSession
import tomli_w

from axis.models.configuration import Configuration


async def main_async(args: argparse.Namespace) -> int:
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


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the Axis CLI.

    Returns:
        argparse.Namespace: Parsed arguments with host, username, password, and output file.

    """
    parser = argparse.ArgumentParser(
        description="Axis CLI: Validate configuration and export to TOML."
    )
    parser.add_argument("--host", required=True, help="Device hostname or IP address.")
    parser.add_argument(
        "--username", required=True, help="Username for device authentication."
    )
    parser.add_argument(
        "--password", required=True, help="Password for device authentication."
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Path to output TOML file.",
    )
    return parser.parse_args()


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
    """Run the synchronous entry point for the CLI.

    Parses arguments and runs the async main logic.
    """
    args = parse_args()
    exit_code = asyncio.run(main_async(args))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
