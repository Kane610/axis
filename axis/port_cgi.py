"""Axis Vapix port management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10074527

I/O port API. Digital input and output ports.
General purpose I/O service API. Extends I/O port API with support for
    supervised I/Os and relay connectors.
Virtual input API.
"""
import re

from .api import APIItems
from .param_cgi import IOPORT

PROPERTY = 'Properties.API.HTTP.Version=3'

URL = '/axis-cgi/io/port.cgi'
URL_GET = URL + '?action=list'
URL_GET_GROUP = URL_GET + '&group={group}'

REGEX_PORT_INDEX = re.compile(r'\d+')


class Ports(APIItems):
    """Represents all ports of io/port.cgi."""

    def __init__(self, param_cgi: object, request: str) -> None:
        self.param_cgi = param_cgi
        raw = self.param_cgi.ports
        super().__init__(raw, request, URL_GET, Port)

    def update(self) -> None:
        self.param_cgi.update_ports()
        raw = self.param_cgi.ports
        self.process_raw(raw)

    def process_raw(self, raw: dict) -> None:
        """Pre-process raw dict.

        Prepare parameters to work with APIItems.
        """
        raw_ports = {}

        for param in raw:
            idx = REGEX_PORT_INDEX.search(param).group(0)

            if idx not in raw_ports:
                raw_ports[idx] = {}

            name = param.replace(IOPORT + '.I' + idx + '.', '')
            raw_ports[idx][name] = raw[param]

        super().process_raw(raw_ports)


class Port:
    """Represents a port."""

    def __init__(self, id: str, raw: dict, request: str) -> None:
        self.id = id
        self.raw = raw
        self._request = request

    @property
    def configurable(self) -> str:
        """The port is configurable or not."""
        return self.raw['Configurable']

    @property
    def direction(self) -> str:
        """The port is configured to act as input or output.

        Read-only for non-configurable ports.
        """
        return self.raw['Direction']

    @property
    def input_name(self) -> str:
        """User-friendly name for the input."""
        return self.raw['Input.Name']

    @property
    def input_trig(self) -> str:
        """Determines when to trig.

        closed=The input port triggers when the circuit is closed.
        open=The input port triggers when the circuit is open.
        """
        return self.raw['Input.Trig']

    @property
    def output_name(self) -> str:
        """User-friendly name for the output."""
        return self.raw['Output.Name']

    @property
    def output_active(self) -> str:
        """The active state of the output.

        closed=The output port is active when the circuit is closed.
        open=The output port is active when the circuit is open.
        """
        return self.raw['Output.Active']
