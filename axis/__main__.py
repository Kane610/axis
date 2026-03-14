"""Read events and parameters from your Axis device."""

import argparse
import asyncio
import logging
from typing import TYPE_CHECKING, cast

import aiohttp
from httpx import AsyncClient

import axis
from axis.device import AxisDevice
from axis.models.configuration import Configuration, WebProtocol

if TYPE_CHECKING:
    from axis.models.configuration import HTTPSession
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
    http_client: str = "httpx",
    is_companion: bool = False,
) -> axis.device.AxisDevice:
    """Create a Axis device."""
    session = create_session(http_client)
    device = AxisDevice(
        Configuration(
            session,
            host,
            port=port,
            username=username,
            password=password,
            is_companion=is_companion,
            web_proto=web_proto,
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

    except (TimeoutError, axis.RequestError):
        LOGGER.error("Error connecting to the Axis device at %s", host)

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
    http_client: str,
) -> None:
    """CLI method for library."""
    LOGGER.info("Connecting to Axis device")

    device = await axis_device(
        host,
        port,
        username,
        password,
        web_proto=web_proto,
        http_client=http_client,
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


def create_session(http_client: str) -> HTTPSession:
    """Create HTTP session based on selected backend."""
    if http_client == "aiohttp":
        connector = aiohttp.TCPConnector(ssl=False)
        return cast("HTTPSession", aiohttp.ClientSession(connector=connector))

    return cast("HTTPSession", AsyncClient(verify=False))  # noqa: S501


async def close_session(session: HTTPSession) -> None:
    """Close session regardless of selected HTTP backend."""
    if isinstance(session, aiohttp.ClientSession):
        await session.close()
        return

    await cast("AsyncClient", session).aclose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host", type=str)
    parser.add_argument("username", type=str)
    parser.add_argument("password", type=str)
    parser.add_argument("-p", "--port", type=int, default=0)
    parser.add_argument("--proto", type=str, default="http")
    parser.add_argument("--events", action="store_true")
    parser.add_argument("--params", action="store_true")
    parser.add_argument("--http-client", choices=("httpx", "aiohttp"), default="httpx")
    parser.add_argument("-D", "--debug", action="store_true")
    args = parser.parse_args()

    loglevel = logging.INFO
    if args.debug:
        loglevel = logging.DEBUG
    logging.basicConfig(format="%(message)s", level=loglevel)

    LOGGER.info(
        "%s, %s, %s, %s, %s, %s",
        args.host,
        args.username,
        args.password,
        args.port,
        args.events,
        args.params,
    )

    try:
        asyncio.run(
            main(
                host=args.host,
                username=args.username,
                password=args.password,
                port=args.port,
                params=args.params,
                events=args.events,
                web_proto=WebProtocol(args.proto),
                http_client=args.http_client,
            )
        )

    except KeyboardInterrupt:
        LOGGER.info("Keyboard interrupt")
