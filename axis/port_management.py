"""I/O Port Management API.

The I/O port management API makes it possible to retrieve information about the ports and apply product dependent configurations
"""

import attr

from .api import APIItem, APIItems, Body

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


class IoPortManagement(APIItems):
    """I/O port management for Axis devices."""

    def __init__(self, request: object) -> None:
        super().__init__({}, request, URL, Port)

    def update(self, path=None) -> None:
        raw = self.get_ports()
        if raw["data"]["numberOfPorts"] > 0:
            self.process_raw(raw["data"]["items"])

    def process_raw(self, raw: list) -> None:
        """Pre-process raw json dict.

        Prepare parameters to work with APIItems.
        """
        raw_ports = {port["port"]: port for port in raw}

        super().process_raw(raw_ports)

    def get_ports(self) -> dict:
        """This CGI method can be used to retrieve information about all ports on the device and their capabilities."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("getPorts", API_VERSION),
                filter=attr.filters.exclude(attr.fields(Body).params),
            ),
        )

    def set_ports(self, ports: list) -> None:
        """Configures anything from one to several ports.

        Some of the available options are:
        * Setting a nice name that can be used in the user interface.
        * Configuring the states and what constitutes a normal and triggered state respectively.
            This will make triggers activate in either open or closed circuits.
        The reason the change is treated as a nice name is because it doesn’t affect the underlying behavior of the port.
        Devices with configurable ports can change the direction to either input or output.
        """
        self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("setPorts", API_VERSION, params=ports),
                filter=lambda attr, value: value is not None,
            ),
        )

    def set_state_sequence(self, sequence: PortSequence) -> None:
        """Applies a sequence of state changes with a delay in milliseconds between states."""
        self._request(
            "post",
            URL,
            json=attr.asdict(Body("setStateSequence", API_VERSION, params=sequence)),
        )

    def get_supported_versions(self) -> dict:
        """This CGI method can be used to retrieve a list of supported API versions."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("getSupportedVersions", API_VERSION),
                filter=attr.filters.include(attr.fields(Body).method),
            ),
        )


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
        """Normal state of port.

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

    def set_state(self, set_port: SetPort):
        """Set port state."""
        self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("setPorts", API_VERSION, params=[set_port]),
                filter=lambda attr, value: value is not None,
            ),
        )

    def open(self):
        """Open port."""
        self.set_state(SetPort(self.port, state="open"))

    def close(self):
        """Close port."""
        self.set_state(SetPort(self.port, state="closed"))
