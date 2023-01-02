"""I/O Port Management API.

The I/O port management API makes it possible to retrieve information about the ports and apply product dependent configurations
"""

import attr

from ..models.port_management import Port, PortSequence
from ..models.port_management import Sequence  # noqa: F401
from ..models.port_management import SetPort  # noqa: F401
from .api import APIItems, Body

URL = "/axis-cgi/io/portmanagement.cgi"

API_DISCOVERY_ID = "io-port-management"
API_VERSION = "1.0"


class IoPortManagement(APIItems):
    """I/O port management for Axis devices."""

    item_cls = Port
    path = URL

    async def update(self) -> None:
        """Refresh data."""
        raw = await self.get_ports()
        self.process_raw(raw)

    @staticmethod
    def pre_process_raw(raw: dict) -> dict:
        """Return a dictionary of ports."""
        if not raw:
            return {}

        if raw.get("data", {}).get("numberOfPorts", 0) == 0:
            return {}

        ports = raw["data"]["items"]
        return {port["port"]: port for port in ports}

    async def get_ports(self) -> dict:
        """Retrieve information about all ports on the device and their capabilities."""
        return await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body("getPorts", API_VERSION),
                filter=attr.filters.exclude(attr.fields(Body).params),
            ),
        )

    async def set_ports(self, ports: list) -> None:
        """Configure one or more ports.

        Some of the available options are:
        * Setting a nice name that can be used in the user interface.
        * Configuring the states and what constitutes a normal and triggered state respectively.
            This will make triggers activate in either open or closed circuits.
        The reason the change is treated as a nice name is because it doesn’t affect the underlying behavior of the port.
        Devices with configurable ports can change the direction to either input or output.
        """
        await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body("setPorts", API_VERSION, params=ports),
                filter=lambda attr, value: value is not None,
            ),
        )

    async def set_state_sequence(self, sequence: PortSequence) -> None:
        """Apply a sequence of state changes with a delay in milliseconds between states."""
        await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(Body("setStateSequence", API_VERSION, params=sequence)),
        )

    async def get_supported_versions(self) -> dict:
        """Retrieve a list of supported API versions."""
        return await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body("getSupportedVersions", API_VERSION),
                filter=attr.filters.include(attr.fields(Body).method),
            ),
        )
