"""Test Axis I/O port management API.

pytest --cov-report term-missing --cov=axis.port_management tests/test_port_management.py
"""

import json

import pytest

from axis.interfaces.port_management import IoPortManagement
from axis.models.port_management import PortConfiguration, Sequence


@pytest.fixture
def io_port_management(axis_device) -> IoPortManagement:
    """Return the io_port_management mock object."""
    return IoPortManagement(axis_device.vapix)


async def test_get_ports(respx_mock, io_port_management):
    """Test get_ports call."""
    route = respx_mock.post("/axis-cgi/io/portmanagement.cgi").respond(
        json=GET_PORTS_RESPONSE,
    )

    await io_port_management.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/io/portmanagement.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "apiVersion": "1.0",
        "context": "Axis library",
        "method": "getPorts",
    }

    assert io_port_management.initialized
    assert len(io_port_management.values()) == 1

    item = io_port_management["0"]
    assert item.id == "0"
    assert item.name == "PIR sensor"
    assert item.configurable is False
    assert item.usage == ""
    assert item.direction == "input"
    assert item.state == "open"
    assert item.normal_state == "open"

    await io_port_management.open("0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/io/portmanagement.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "setPorts",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"ports": [{"port": "0", "state": "open"}]},
    }

    await io_port_management.close("0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/io/portmanagement.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "setPorts",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"ports": [{"port": "0", "state": "closed"}]},
    }


async def test_get_empty_ports_response(respx_mock, io_port_management):
    """Test get_ports call."""
    respx_mock.post("/axis-cgi/io/portmanagement.cgi").respond(
        json=GET_EMPTY_PORTS_RESPONSE,
    )
    await io_port_management.update()
    assert io_port_management.initialized
    assert len(io_port_management.values()) == 0


async def test_set_ports(respx_mock, io_port_management):
    """Test set_ports call."""
    route = respx_mock.post("/axis-cgi/io/portmanagement.cgi")

    await io_port_management.set_ports(
        [
            PortConfiguration(
                "0",
                usage="",
                direction="",
                name="",
                normal_state="",
                state="closed",
            )
        ]
    )

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/io/portmanagement.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "setPorts",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {
            "ports": [
                {
                    "port": "0",
                    "usage": "",
                    "direction": "",
                    "name": "",
                    "normalState": "",
                    "state": "closed",
                }
            ]
        },
    }


async def test_set_state_sequence(respx_mock, io_port_management):
    """Test setting state sequence call."""
    route = respx_mock.post("/axis-cgi/io/portmanagement.cgi")

    await io_port_management.set_state_sequence(
        "0", [Sequence("open", 3000), Sequence("closed", 5000)]
    )

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/io/portmanagement.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "setStateSequence",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {
            "port": "0",
            "sequence": [
                {"state": "open", "time": 3000},
                {"state": "closed", "time": 5000},
            ],
        },
    }


async def test_get_supported_versions(respx_mock, io_port_management):
    """Test get_supported_versions."""
    route = respx_mock.post("/axis-cgi/io/portmanagement.cgi").respond(
        json=GET_SUPPORTED_VERSIONS_RESPONSE,
    )

    response = await io_port_management.get_supported_versions()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/io/portmanagement.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getSupportedVersions",
        "context": "Axis library",
    }
    assert response == ["1.0"]


GET_PORTS_RESPONSE = {
    "apiVersion": "1.0",
    "context": "Retrieve all properties of available ports",
    "method": "getPorts",
    "data": {
        "numberOfPorts": 1,
        "items": [
            {
                "port": "0",
                "configurable": False,
                "usage": "",
                "name": "PIR sensor",
                "direction": "input",
                "state": "open",
                "normalState": "open",
            }
        ],
    },
}

GET_EMPTY_PORTS_RESPONSE = {
    "apiVersion": "1.0",
    "context": "Axis library",
    "method": "getPorts",
    "data": {"numberOfPorts": 0},
}

GET_SUPPORTED_VERSIONS_RESPONSE = {
    "apiVersion": "1.0",
    "context": "",
    "method": "getSupportedVersions",
    "data": {"apiVersions": ["1.0"]},
}
