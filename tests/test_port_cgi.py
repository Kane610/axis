"""Test Axis parameter management.

pytest --cov-report term-missing --cov=axis.port_cgi tests/test_port_cgi.py
"""

from unittest.mock import AsyncMock

from axis.param_cgi import Params
from axis.port_cgi import ACTION_LOW, Ports


async def test_ports():
    """Test that different types of ports work."""
    mock_request = AsyncMock()
    mock_request.return_value = fixture_ports
    params = Params(mock_request)
    ports = Ports(params, mock_request)
    await ports.update()

    mock_request.assert_called_once

    assert ports["0"].id == "0"
    assert ports["0"].configurable == "no"
    assert ports["0"].direction == "input"
    assert not ports["0"].name

    await ports["0"].action(action=ACTION_LOW)
    mock_request.assert_called_once

    assert ports["1"].id == "1"
    assert ports["1"].configurable == "no"
    assert ports["1"].direction == "input"
    assert ports["1"].name == "PIR sensor"
    assert ports["1"].input_trig == "closed"

    assert ports["2"].id == "2"
    assert ports["2"].configurable == "no"
    assert ports["2"].direction == "input"
    assert ports["2"].name == ""
    assert ports["2"].output_active == "closed"

    assert ports["3"].id == "3"
    assert ports["3"].configurable == "no"
    assert ports["3"].direction == "output"
    assert ports["3"].name == "Tampering"
    assert ports["3"].output_active == "open"

    await ports["3"].close()
    mock_request.assert_called_with("get", "/axis-cgi/io/port.cgi?action=4%3A%2F")

    await ports["3"].open()
    mock_request.assert_called_with("get", "/axis-cgi/io/port.cgi?action=4%3A%5C")


async def test_no_ports():
    """Test that no ports also work."""
    mock_request = AsyncMock()
    mock_request.return_value = ""
    params = Params(mock_request)
    ports = Ports(params, mock_request)
    await ports.update()

    mock_request.assert_called_once

    assert len(ports.values()) == 0


fixture_ports = """root.IOPort.I0.Direction=input
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
"""
