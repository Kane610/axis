# ruff: noqa: D100,D101,D102

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
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


@dataclass
class CliRouter:
    nodes: dict[str, MenuNode] = field(default_factory=dict)

    def register_node(self, node: MenuNode) -> None:
        self.nodes[node.id] = node

    async def run(
        self, ctx: CliContext, io: CliIO, start_node_id: str = "main"
    ) -> None:
        current = start_node_id
        while True:
            node = self.nodes[current]
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

            # Commands are intentionally not executed here yet to keep routing
            # simple and preserve current flow compatibility in main.py.
            io.write("Command execution is handled by composed workflows.")
