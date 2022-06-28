"""I/O Port Management API.

The I/O port management API makes it possible to retrieve information about the ports and apply product dependent configurations
"""

import attr

from ..interfaces.api import Body
from .api import APIItem

URL = "/axis-cgi/io/portmanagement.cgi"

API_DISCOVERY_ID = "io-port-management"
API_VERSION = "1.0"


@attr.s
class SetPort:
    """Port configuration class."""

    port: str = attr.ib()
    usage: str = attr.ib(default=None)
    direction: str = attr.ib(default=None)
    name: str = attr.ib(default=None)
    normalState: str = attr.ib(default=None)
    state: str = attr.ib(default=None)


@attr.s
class PortSequence:
    """Port sequence class."""

    port: str = attr.ib()
    sequence: list = attr.ib(factory=list)


@attr.s
class Sequence:
    """Sequence class."""

    state: str = attr.ib()
    time: int = attr.ib()


class Port(APIItem):
    """I/O port management port."""

    @property
    def configurable(self) -> bool:
        """Is port configurable."""
        return self.raw["configurable"]

    @property
    def direction(self) -> str:
        """Direction of port.

        <input|output>.
        """
        return self.raw["direction"]

    @property
    def name(self) -> str:
        """Name of port."""
        return self.raw["name"]

    @property
    def normalState(self) -> str:
        """Port normal state.

        <open|closed>.
        """
        return self.raw["normalState"]

    @property
    def port(self) -> str:
        """Index of port."""
        return self.raw["port"]

    @property
    def state(self) -> str:
        """State of port.

        <open|closed>.
        """
        return self.raw["state"]

    @property
    def usage(self) -> str:
        """Usage of port."""
        return self.raw["usage"]

    async def set_state(self, set_port: SetPort) -> None:
        """Set port state."""
        await self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("setPorts", API_VERSION, params=[set_port]),
                filter=lambda attr, value: value is not None,
            ),
        )

    async def open(self) -> None:
        """Open port."""
        await self.set_state(SetPort(self.port, state="open"))

    async def close(self) -> None:
        """Close port."""
        await self.set_state(SetPort(self.port, state="closed"))
