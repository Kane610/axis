"""Read events and parameters from your Axis device."""

import asyncio
import logging
from typing import TYPE_CHECKING

import aiohttp

import axis
from axis.device import AxisDevice
from axis.models.configuration import Configuration, WebProtocol

if TYPE_CHECKING:
    from axis.models.event import Event

LOGGER = logging.getLogger(__name__)


def event_handler(event: Event) -> None:
    """Receive and print events from RTSP stream."""
    LOGGER.info(event)


async def axis_device(
    host: str,
    port: int,
    username: str,
    password: str,
    web_proto: WebProtocol,
    stream_mode: str = "rtsp",
    is_companion: bool = False,
) -> axis.device.AxisDevice:
    """Create a Axis device."""
    session = create_session()
    websocket_enabled, websocket_force = websocket_flags_from_mode(stream_mode)
    device = AxisDevice(
        Configuration(
            session,
            host,
            port=port,
            username=username,
            password=password,
            is_companion=is_companion,
            web_proto=web_proto,
            websocket_enabled=websocket_enabled,
            websocket_force=websocket_force,
        )
    )

    try:
        async with asyncio.timeout(5):
            await device.vapix.initialize_users()
            await device.vapix.load_user_groups()
        # await device.vapix.initialize_event_instances()

        return device

    except axis.Unauthorized:
        LOGGER.warning(
            "Connected to device at %s but not registered or user not admin.", host
        )

    except (TimeoutError, axis.RequestError) as err:
        LOGGER.error("Error connecting to the Axis device at %s: %s", host, err)

    except axis.AxisException:
        LOGGER.exception("Unknown Axis communication error occurred")

    return device


async def main(
    host: str,
    port: int,
    username: str,
    password: str,
    params: bool,
    events: bool,
    web_proto: WebProtocol,
    stream_mode: str,
) -> None:
    """CLI method for library."""
    LOGGER.info("Connecting to Axis device")

    device = await axis_device(
        host,
        port,
        username,
        password,
        web_proto=web_proto,
        stream_mode=stream_mode,
    )

    if not device:
        LOGGER.error("Couldn't connect to Axis device")
        return

    if params:
        await device.vapix.initialize()

    if events:
        device.enable_events()
        device.event.subscribe(event_handler)
        device.stream.start()

    try:
        if events:
            done = asyncio.Event()
            await done.wait()

    except asyncio.CancelledError:
        device.stream.stop()

    finally:
        await close_session(device.config.session)
        device.stream.stop()


def create_session() -> aiohttp.ClientSession:
    """Create aiohttp session used for HTTP requests."""
    connector = aiohttp.TCPConnector(ssl=False)
    return aiohttp.ClientSession(connector=connector)


async def close_session(session: aiohttp.ClientSession) -> None:
    """Close aiohttp session."""
    await session.close()


def websocket_flags_from_mode(stream_mode: str) -> tuple[bool, bool]:
    """Translate CLI stream mode to websocket enable/force flags."""
    if stream_mode == "auto":
        return True, False
    if stream_mode == "event":
        return True, True
    return False, False


if __name__ == "__main__":
    from axis.cli.entrypoint import main as run_cli

    run_cli()
