"""Test Axis parameter management.

pytest --cov-report term-missing --cov=axis.port_cgi tests/test_port_cgi.py
"""

import pytest

from axis.interfaces.port_cgi import Ports
from axis.models.parameters.io_port import PortAction, PortDirection

from .conftest import HOST


@pytest.fixture
def ports(axis_device) -> Ports:
    """Return the api_discovery mock object."""
    return axis_device.vapix.port_cgi


async def test_ports(respx_mock, ports: Ports) -> None:
    """Test that different types of ports work."""
    update_ports_route = respx_mock.post(f"http://{HOST}/axis-cgi/param.cgi").respond(
        text="""root.Input.NbrOfInputs=3
root.IOPort.I0.Direction=input
root.IOPort.I0.Usage=Button
root.IOPort.I1.Configurable=no
root.IOPort.I1.Direction=input
root.IOPort.I1.Input.Name=PIR sensor
root.IOPort.I1.Input.Trig=closed
root.IOPort.I2.Direction=input
root.IOPort.I2.Usage=
root.IOPort.I2.Output.Active=closed
root.IOPort.I2.Output.Button=none
root.IOPort.I2.Output.DelayTime=0
root.IOPort.I2.Output.Mode=bistable
root.IOPort.I2.Output.Name=Output 2
root.IOPort.I2.Output.PulseTime=0
root.IOPort.I3.Direction=output
root.IOPort.I3.Usage=Tampering
root.IOPort.I3.Output.Active=open
root.IOPort.I3.Output.Button=none
root.IOPort.I3.Output.DelayTime=0
root.IOPort.I3.Output.Mode=bistable
root.IOPort.I3.Output.Name=Tampering
root.IOPort.I3.Output.PulseTime=0
root.Output.NbrOfOutputs=1
""",
        headers={"Content-Type": "text/plain"},
    )

    await ports.update()

    assert update_ports_route.call_count == 1

    assert ports["0"].id == "0"
    assert ports["0"].configurable is False
    assert ports["0"].direction == PortDirection.IN
    assert ports["0"].name == ""

    await ports.action("0", action=PortAction.LOW)

    assert ports["1"].id == "1"
    assert ports["1"].configurable is False
    assert ports["1"].direction == PortDirection.IN
    assert ports["1"].name == "PIR sensor"
    assert ports["1"].input_trigger == "closed"

    assert ports["2"].id == "2"
    assert ports["2"].configurable is False
    assert ports["2"].direction == PortDirection.IN
    assert ports["2"].name == ""
    assert ports["2"].output_active == "closed"

    assert ports["3"].id == "3"
    assert ports["3"].configurable is False
    assert ports["3"].direction == PortDirection.OUT
    assert ports["3"].name == "Tampering"
    assert ports["3"].output_active == "open"

    action_low_route = respx_mock.get("/axis-cgi/io/port.cgi?action=4%3A%2F")
    action_high_route = respx_mock.get("/axis-cgi/io/port.cgi?action=4%3A%5C")

    assert not action_low_route.called
    assert not action_high_route.called

    await ports.close("3")
    assert action_low_route.called
    assert action_low_route.calls.last.request.method == "GET"
    assert action_low_route.calls.last.request.url.path == "/axis-cgi/io/port.cgi"
    assert action_low_route.calls.last.request.url.query.decode() == "action=4%3A%2F"

    await ports.open("3")
    assert action_high_route.called
    assert action_high_route.calls.last.request.method == "GET"
    assert action_high_route.calls.last.request.url.path == "/axis-cgi/io/port.cgi"
    assert action_high_route.calls.last.request.url.query.decode() == "action=4%3A%5C"


async def test_no_ports(respx_mock, ports: Ports) -> None:
    """Test that no ports also work."""
    route = respx_mock.post(f"http://{HOST}/axis-cgi/param.cgi").respond(
        text="",
        headers={"Content-Type": "text/plain"},
    )

    await ports.update()

    assert route.call_count == 1
    assert len(ports.values()) == 0


@pytest.mark.parametrize(
    ("enum", "input", "output"),
    [
        (PortAction, "/", PortAction.HIGH),
        (PortAction, "\\", PortAction.LOW),
        (PortAction, ".", PortAction.UNKNOWN),
        (PortDirection, "input", PortDirection.IN),
        (PortDirection, "output", PortDirection.OUT),
        (PortDirection, ".", PortDirection.UNKNOWN),
    ],
)
def test_enums(enum, input, output) -> None:
    """Validate enum values."""
    assert enum(input) == output
