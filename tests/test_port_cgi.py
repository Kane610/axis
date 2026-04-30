"""Test Axis parameter management.

pytest --cov-report term-missing --cov=axis.port_cgi tests/test_port_cgi.py
"""

from __future__ import annotations

import aiohttp
import pytest

from axis.device import AxisDevice
from axis.models.configuration import Configuration
from axis.models.parameters.io_port import PortAction, PortDirection

from .conftest import HOST, PASS, USER


async def test_ports(aiohttp_mock_server) -> None:
    """Test that different types of ports work."""
    session = aiohttp.ClientSession()
    axis_device = AxisDevice(
        Configuration(
            session,
            HOST,
            port=80,
            username=USER,
            password=PASS,
        )
    )

    _server, requests = await aiohttp_mock_server(
        {
            "/axis-cgi/param.cgi": {
                "method": "POST",
                "response": """root.Input.NbrOfInputs=3
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
""".encode("iso-8859-1"),
                "headers": {"Content-Type": "text/plain; charset=iso-8859-1"},
            },
            "/axis-cgi/io/port.cgi": {"method": "GET", "response": ""},
        },
        device=axis_device,
    )
    ports = axis_device.vapix.port_cgi

    try:
        await ports.update()
        assert requests is not None
        assert (
            len(
                [
                    req
                    for req in requests
                    if req["method"] == "POST" and req["path"] == "/axis-cgi/param.cgi"
                ]
            )
            == 1
        )

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

        io_requests = [
            req
            for req in requests
            if req["method"] == "GET" and req["path"] == "/axis-cgi/io/port.cgi"
        ]
        low_count = len(io_requests)
        await ports.close("3")
        io_requests = [
            req
            for req in requests
            if req["method"] == "GET" and req["path"] == "/axis-cgi/io/port.cgi"
        ]
        assert len(io_requests) == low_count + 1
        assert io_requests[-1]["query"] == "action=4:/"

        high_count = len(io_requests)
        await ports.open("3")
        io_requests = [
            req
            for req in requests
            if req["method"] == "GET" and req["path"] == "/axis-cgi/io/port.cgi"
        ]
        assert len(io_requests) == high_count + 1
        assert io_requests[-1]["query"] == "action=4:\\"
    finally:
        await session.close()


async def test_no_ports(aiohttp_mock_server) -> None:
    """Test that no ports also work."""
    session = aiohttp.ClientSession()
    axis_device = AxisDevice(
        Configuration(
            session,
            HOST,
            port=80,
            username=USER,
            password=PASS,
        )
    )
    _server, requests = await aiohttp_mock_server(
        "/axis-cgi/param.cgi",
        method="POST",
        response="".encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
        device=axis_device,
    )
    ports = axis_device.vapix.port_cgi

    try:
        await ports.update()
        assert requests is not None
        assert (
            len(
                [
                    req
                    for req in requests
                    if req["method"] == "POST" and req["path"] == "/axis-cgi/param.cgi"
                ]
            )
            == 1
        )
        assert len(ports.values()) == 0
    finally:
        await session.close()


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
