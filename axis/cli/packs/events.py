# ruff: noqa: D100,D103

from __future__ import annotations

import asyncio
import os
from pprint import pformat
from typing import TYPE_CHECKING

from aiohttp import ClientSession

from axis.cli.core.contracts import CommandCapabilities, CommandResult
from axis.cli.core.router import MenuItem, MenuNode
from axis.cli.packs.devices import (
    DeviceEntry,
    _format_device_operations_label,
    get_device_credentials,
    run_on_selected_device,
)
from axis.device import AxisDevice
from axis.errors import RequestError
from axis.models.configuration import Configuration

if TYPE_CHECKING:
    from axis.cli.core.context import CliContext
    from axis.cli.core.io import CliIO
    from axis.cli.core.registry import CommandRegistry
    from axis.cli.core.router import CliRouter


class _EventsMenuCommand:
    id = "events.menu"
    title = "Event instances & live listen"
    capabilities = CommandCapabilities(requires_device=True)

    async def run(self, ctx: CliContext, io: CliIO) -> CommandResult:
        _ = io
        if ctx.selected_serial is None or ctx.selected_device is None:
            return CommandResult(
                status="cancelled",
                message="No selected device in context.",
            )
        events_flow(ctx.selected_serial, ctx.selected_device)
        return CommandResult()


def _debug_enabled() -> bool:
    value = os.getenv("AXIS_CLI_DEBUG", "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def _debug_dump(label: str, payload: object) -> None:
    if _debug_enabled():
        print(f"[debug] {label}:\n{pformat(payload)}")  # noqa: T201


def _render_events_node(ctx: CliContext, io: CliIO) -> None:
    if ctx.selected_serial is None or ctx.selected_device is None:
        io.write("\nNo selected device.")
        return

    device_label = _format_device_operations_label(
        ctx.selected_serial,
        ctx.selected_device,
    )
    io.write(f"\nEvents for {device_label}:")


def register(registry: CommandRegistry, router: CliRouter) -> None:
    """Register event-pack commands and menu nodes."""
    registry.register_command(_EventsMenuCommand())

    router.register_node(
        MenuNode(
            id="events",
            title="Events",
            parent_id="device_operations",
            render=_render_events_node,
            items=[
                MenuItem(
                    key="1",
                    label="Event instances & live listen",
                    action="command",
                    command_id="events.menu",
                )
            ],
        )
    )


async def fetch_event_instances(device_entry: DeviceEntry) -> list[dict[str, str]]:
    async def _operation(device: AxisDevice) -> list[dict[str, str]]:
        await device.vapix.event_instances.update()
        return [
            {
                "topic": ev.topic,
                "name": ev.name,
                "stateful": str(ev.stateful),
                "stateless": str(ev.stateless),
                "available": str(ev.is_available),
            }
            for ev in device.vapix.event_instances.values()
        ]

    result = await run_on_selected_device(device_entry, _operation)
    return result if result is not None else []


def list_event_instances_flow(
    serial: str, device_entry: DeviceEntry
) -> list[dict[str, str]]:
    events = asyncio.run(fetch_event_instances(device_entry))
    _debug_dump("event instances", events)
    if not events:
        print(f"No event instances found for {serial}.")  # noqa: T201
        return []

    device_label = _format_device_operations_label(serial, device_entry)
    print(f"\nEvent instances for {device_label}:")  # noqa: T201

    rows: list[tuple[str, str, str, str]] = []
    for _idx, ev in enumerate(events, 1):
        is_stateful = ev["stateful"] == "True"
        is_stateless = ev["stateless"] == "True"
        if is_stateful and is_stateless:
            state = "stateful/stateless"
        elif is_stateful:
            state = "stateful"
        elif is_stateless:
            state = "stateless"
        else:
            state = "none"

        available = "yes" if ev["available"] == "True" else "no"
        name = ev["name"].strip() if ev["name"].strip() else "<unnamed>"
        rows.append((name, ev["topic"], state, available))

    name_width = max(len("name"), *(len(row[0]) for row in rows))
    topic_width = max(len("topic"), *(len(row[1]) for row in rows))
    state_width = max(len("state"), *(len(row[2]) for row in rows))
    available_width = max(len("available"), *(len(row[3]) for row in rows))

    print(  # noqa: T201
        f"  {'#':>2}  {'name':<{name_width}}  {'topic':<{topic_width}}"
        f"  {'state':<{state_width}}  {'available':<{available_width}}"
    )
    print(  # noqa: T201
        f"  {'-' * (16 + name_width + topic_width + state_width + available_width)}"
    )

    for idx, (name, topic, state, available) in enumerate(rows, 1):
        print(  # noqa: T201
            f"  {idx:>2}. {name:<{name_width}}  {topic:<{topic_width}}"
            f"  {state:<{state_width}}  {available:<{available_width}}"
        )
    return events


def _live_listen_flow(device_entry: DeviceEntry, topic_filter: str | None) -> None:
    credentials = get_device_credentials(device_entry)
    if credentials is None:
        print("Stored device config is incomplete. Please re-add the device.")  # noqa: T201
        return

    if topic_filter:
        print(f"\nListening for events on topic '{topic_filter}' (Ctrl+C to stop)...")  # noqa: T201
    else:
        print("\nListening for all events (Ctrl+C to stop)...")  # noqa: T201

    async def _run_listener() -> None:
        async with ClientSession() as session:
            config = Configuration(
                session=session,
                host=credentials["host"],
                username=credentials["username"],
                password=credentials["password"],
            )
            device = AxisDevice(config)

            def _on_event(event: object) -> None:
                print(f"  [event] {event}")  # noqa: T201

            unsubscribe = device.event.subscribe(
                callback=_on_event,
                id_filter=topic_filter,
            )
            stop_event = asyncio.Event()
            try:
                device.enable_events()
                await stop_event.wait()
            except asyncio.CancelledError:
                pass
            finally:
                unsubscribe()

    try:
        asyncio.run(_run_listener())
    except KeyboardInterrupt:
        print("\nStopped listening.")  # noqa: T201
    except RequestError as exc:
        print(f"Device request failed: {exc}")  # noqa: T201


def events_flow(serial: str, device_entry: DeviceEntry) -> None:
    device_label = _format_device_operations_label(serial, device_entry)
    while True:
        print(f"\nEvent options for {device_label}:")  # noqa: T201
        print("  1. List event instances")  # noqa: T201
        print("  2. Listen to events (all topics)")  # noqa: T201
        print("  3. Listen to events (select topic)")  # noqa: T201
        print("  b. Back")  # noqa: T201
        print("  e. Exit")  # noqa: T201
        choice = input("Select option [1/2/3/b/e]: ").strip().lower()

        if choice == "e":
            print("Exiting.")  # noqa: T201
            raise SystemExit(0)
        if choice == "b":
            return

        if choice == "1":
            list_event_instances_flow(serial, device_entry)
            continue

        if choice == "2":
            _live_listen_flow(device_entry, topic_filter=None)
            continue

        if choice == "3":
            events = list_event_instances_flow(serial, device_entry)
            if not events:
                continue
            topic_choice = input("Enter event number to filter by: ").strip()
            try:
                topic_idx = int(topic_choice)
            except ValueError:
                print("Invalid selection.")  # noqa: T201
                continue
            if topic_idx < 1 or topic_idx > len(events):
                print("Invalid selection.")  # noqa: T201
                continue
            selected_topic = events[topic_idx - 1]["topic"]
            _live_listen_flow(device_entry, topic_filter=selected_topic)
            continue

        print("Invalid option. Please enter 1, 2, 3, b, or e.")  # noqa: T201
