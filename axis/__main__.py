"""Read events and parameters from your Axis device."""

import argparse
import asyncio
import logging

import async_timeout
from httpx import AsyncClient

import axis

LOGGER = logging.getLogger(__name__)


def event_handler(action, event):
    """Receive and print events from RTSP stream."""
    LOGGER.info(f"{action} {event}")


async def axis_device(
    host: str, port: int, username: str, password: str
) -> axis.AxisDevice:
    """Create a Axis device."""
    session = AsyncClient(verify=False)
    device = axis.AxisDevice(
        axis.configuration.Configuration(
            session, host, port=port, username=username, password=password
        )
    )

    try:
        async with async_timeout.timeout(5):
            await device.vapix.initialize_users()
            await device.vapix.load_user_groups()
        await device.vapix.initialize_event_instances()

        return device

    except axis.Unauthorized:
        LOGGER.warning(
            "Connected to device at %s but not registered or user not admin.", host
        )

    except (asyncio.TimeoutError, axis.RequestError):
        LOGGER.error("Error connecting to the Axis device at %s", host)

    except axis.AxisException:
        LOGGER.exception("Unknown Axis communication error occurred")

    return device


async def main(
    host: str, port: int, username: str, password: str, params: bool, events: bool
) -> None:
    """CLI method for library."""
    LOGGER.info("Connecting to Axis device")

    device = await axis_device(host, port, username, password)

    if not device:
        LOGGER.error("Couldn't connect to Axis device")
        return

    if params:
        await device.vapix.initialize()

    if events:
        device.enable_events(event_callback=event_handler)
        device.stream.start()

    try:
        if events:
            while True:
                await asyncio.sleep(1)

    except asyncio.CancelledError:
        device.stream.stop()
        pass

    finally:
        await device.config.session.aclose()
        device.stream.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host", type=str)
    parser.add_argument("username", type=str)
    parser.add_argument("password", type=str)
    parser.add_argument("-p", "--port", type=int, default=80)
    parser.add_argument("--events", action="store_true")
    parser.add_argument("--params", action="store_true")
    parser.add_argument("-D", "--debug", action="store_true")
    args = parser.parse_args()

    loglevel = logging.INFO
    if args.debug:
        loglevel = logging.DEBUG
    logging.basicConfig(format="%(message)s", level=loglevel)

    LOGGER.info(
        f"{args.host}, {args.username}, {args.password}, {args.port}, {args.events}, {args.params}"
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
            )
        )

    except KeyboardInterrupt:
        pass
