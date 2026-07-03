# ruff: noqa: D100,D101,D102

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from axis.cli.core.context import CliContext
    from axis.cli.core.io import CliIO


@dataclass(frozen=True)
class MenuItem:
    key: str
    label: str
    action: str
    command_id: str | None = None
    next_node_id: str | None = None


@dataclass
class MenuNode:
    id: str
    title: str
    items: list[MenuItem]
    parent_id: str | None = None
    render: Callable[[CliContext, CliIO], None] | None = None


@dataclass
class CliRouter:
    nodes: dict[str, MenuNode] = field(default_factory=dict)

    def register_node(self, node: MenuNode) -> None:
        if node.id in self.nodes:
            msg = f"Node '{node.id}' is already registered."
            raise ValueError(msg)
        self.nodes[node.id] = node

    async def run(
        self, ctx: CliContext, io: CliIO, start_node_id: str = "main"
    ) -> None:
        current = start_node_id
        while True:
            node = self.nodes[current]
            if node.render is not None:
                node.render(ctx, io)
            io.write(f"\n{node.title}:")
            for item in node.items:
                io.write(f"  {item.key}. {item.label}")
            io.write("  b. Back")
            io.write("  e. Exit")
            selection = io.prompt("Select option: ").strip().lower()

            if selection == "e":
                io.write("Exiting.")
                raise SystemExit(0)
            if selection == "b":
                if node.parent_id is None:
                    continue
                current = node.parent_id
                continue

            matched = next((item for item in node.items if item.key == selection), None)
            if matched is None:
                io.write("Invalid option.")
                continue

            if matched.action == "navigate" and matched.next_node_id is not None:
                current = matched.next_node_id
                continue

            if matched.action == "noop":
                continue

            if matched.action == "command":
                if matched.command_id is None:
                    io.write("Command is not configured.")
                    continue

                registry = ctx.command_registry
                if registry is None:
                    io.write("Command registry is unavailable.")
                    continue

                try:
                    command = registry.get_command(matched.command_id)
                except KeyError:
                    io.write(f"Unknown command: {matched.command_id}")
                    continue

                result = await command.run(ctx, io)
                payload = result.payload
                if result.status == "ok" and isinstance(payload, dict):
                    requested_node = payload.get("next_node_id")
                    if isinstance(requested_node, str):
                        if requested_node in self.nodes:
                            if result.message:
                                io.write(result.message)
                            current = requested_node
                            continue
                        io.write(f"Unknown node: {requested_node}")
                if result.message:
                    io.write(result.message)
                elif result.status == "error":
                    io.write("Command failed.")
                elif result.status == "cancelled":
                    io.write("Command cancelled.")
                continue

            io.write("Unsupported action.")
