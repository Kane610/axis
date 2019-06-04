"""Read events and parameters from your Axis device."""

import asyncio
import argparse
import logging
import sys

from axis import AxisDevice


async def main(args):
    loop = asyncio.get_event_loop()
    device = AxisDevice(
        loop=loop, host=args.host, username=args.username,
        password=args.password, port=args.port)

    if args.params:
        await loop.run_in_executor(None, device.vapix.initialize_params)
        await loop.run_in_executor(None, device.vapix.initialize_ports)
        await loop.run_in_executor(None, device.vapix.initialize_users)

        if not args.events:
            return

    if args.events:
        def event_handler(action, event):
            print(action, event)

        device.enable_events(event_callback=event_handler)
        device.start()

    try:
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        pass

    finally:
        device.stop()


if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str)
    parser.add_argument('username', type=str)
    parser.add_argument('password', type=str)
    parser.add_argument('-p', '--port', type=int, default=80)
    parser.add_argument('--events', action='store_true')
    parser.add_argument('--params', action='store_true')
    args = parser.parse_args()

    asyncio.run(main(args))
