"""Test Axis IO port parameter management."""

from typing import TYPE_CHECKING

import pytest

from axis.models.parameters.io_port import PortAction, PortDirection

if TYPE_CHECKING:
    from axis.device import AxisDevice
    from axis.interfaces.parameters.io_port import IOPortParameterHandler

PORT_RESPONSE = """root.IOPort.I0.Configurable=no
root.IOPort.I0.Direction=input
root.IOPort.I0.Input.Name=PIR sensor
root.IOPort.I0.Input.Trig=closed
"""


@pytest.fixture
def io_port_handler(axis_device_aiohttp: AxisDevice) -> IOPortParameterHandler:
    """Return the param cgi mock object."""
    return axis_device_aiohttp.vapix.params.io_port_handler


async def test_port_action_enum():
    """Verify management of unsupported port action."""
    assert PortAction("unsupported") is PortAction.UNKNOWN


async def test_port_direction_enum():
    """Verify management of unsupported port direction."""
    assert PortDirection("unsupported") is PortDirection.UNKNOWN


async def test_io_port_handler(
    aiohttp_mock_server, io_port_handler: IOPortParameterHandler
):
    """Verify that update brand works."""
    _server, _requests = await aiohttp_mock_server(
        "/axis-cgi/param.cgi",
        response=PORT_RESPONSE.encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
        device=io_port_handler,
    )

    assert not io_port_handler.initialized

    await io_port_handler.update()

    assert io_port_handler.initialized
    port = io_port_handler["0"]
    assert not port.configurable
    assert port.direction == "input"
    assert port.name == "PIR sensor"
    assert port.input_trigger == "closed"
    assert port.output_active == ""
