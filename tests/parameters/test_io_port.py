"""Test Axis IO port parameter management."""

import pytest

from axis.device import AxisDevice
from axis.interfaces.parameters.io_port import IOPortParameterHandler
from axis.models.parameters.io_port import PortAction, PortDirection

PORT_RESPONSE = """root.IOPort.I0.Configurable=no
root.IOPort.I0.Direction=input
root.IOPort.I0.Input.Name=PIR sensor
root.IOPort.I0.Input.Trig=closed
"""


@pytest.fixture
def io_port_handler(axis_device: AxisDevice) -> IOPortParameterHandler:
    """Return the param cgi mock object."""
    return axis_device.vapix.params.io_port_handler


async def test_port_action_enum():
    """Verify management of unsupported port action."""
    assert PortAction("unsupported") is PortAction.UNKNOWN


async def test_port_direction_enum():
    """Verify management of unsupported port direction."""
    assert PortDirection("unsupported") is PortDirection.UNKNOWN


async def test_io_port_handler(respx_mock, io_port_handler: IOPortParameterHandler):
    """Verify that update brand works."""
    route = respx_mock.post(
        "/axis-cgi/param.cgi",
        data={"action": "list", "group": "root.IOPort"},
    ).respond(
        content=PORT_RESPONSE.encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
    )
    assert not io_port_handler.initialized

    await io_port_handler.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/param.cgi"

    assert io_port_handler.initialized
    port = io_port_handler["0"]
    assert not port.configurable
    assert port.direction == "input"
    assert port.name == "PIR sensor"
    assert port.input_trigger == "closed"
    assert port.output_active == ""
