"""Test Axis parameter management.

pytest --cov-report term-missing --cov=axis.param_cgi tests/test_param_cgi.py
"""

import pytest
import respx

from axis.device import AxisDevice
from axis.vapix.interfaces.parameters.io_port import IOPortParameterHandler

from ..conftest import HOST

PORT_RESPONSE = """root.IOPort.I0.Configurable=no
root.IOPort.I0.Direction=input
root.IOPort.I0.Input.Name=PIR sensor
root.IOPort.I0.Input.Trig=closed
"""


@pytest.fixture
def io_port_handler(axis_device: AxisDevice) -> IOPortParameterHandler:
    """Return the param cgi mock object."""
    return axis_device.vapix.params.io_port_handler


@respx.mock
async def test_update_ports(io_port_handler: IOPortParameterHandler):
    """Verify that update brand works."""
    route = respx.post(
        f"http://{HOST}:80/axis-cgi/param.cgi",
        data={"action": "list", "group": "root.IOPort"},
    ).respond(
        text=PORT_RESPONSE,
        headers={"Content-Type": "text/plain"},
    )
    await io_port_handler.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/param.cgi"

    assert io_port_handler.supported
    port = io_port_handler["0"]
    assert not port.configurable
    assert port.direction == "input"
    assert port.name == "PIR sensor"
    assert port.input_trigger == "closed"
    assert port.output_active == ""
