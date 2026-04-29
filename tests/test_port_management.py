"""Test Axis I/O port management API.

pytest --cov-report term-missing --cov=axis.port_management tests/test_port_management.py
"""

from aiohttp import web
import pytest

from axis.interfaces.port_management import IoPortManagement
from axis.models.port_management import PortConfiguration, Sequence


@pytest.fixture
def io_port_management(axis_device_aiohttp) -> IoPortManagement:
    """Return the io_port_management mock object."""
    return IoPortManagement(axis_device_aiohttp.vapix)


async def test_get_ports(aiohttp_mock_server, io_port_management):
    """Test get_ports call."""
    requests: list[dict[str, object]] = []

    async def handle_request(request: web.Request) -> web.Response:
        payload = await request.json()
        requests.append(
            {
                "method": request.method,
                "path": request.path,
                "payload": payload,
            }
        )
        if payload["method"] == "getPorts":
            return web.json_response(GET_PORTS_RESPONSE)
        return web.json_response({"apiVersion": "1.0", "context": "Axis library"})

    _server, _captured = await aiohttp_mock_server(
        "/axis-cgi/io/portmanagement.cgi",
        handler=handle_request,
        method="POST",
        device=io_port_management,
    )

    await io_port_management.update()

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/io/portmanagement.cgi"
    assert requests[-1]["payload"] == {
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

    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/io/portmanagement.cgi"
    assert requests[-1]["payload"] == {
        "method": "setPorts",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"ports": [{"port": "0", "state": "open"}]},
    }

    await io_port_management.close("0")

    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/io/portmanagement.cgi"
    assert requests[-1]["payload"] == {
        "method": "setPorts",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"ports": [{"port": "0", "state": "closed"}]},
    }


async def test_get_empty_ports_response(aiohttp_mock_server, io_port_management):
    """Test get_ports call."""
    _server, _requests = await aiohttp_mock_server(
        "/axis-cgi/io/portmanagement.cgi",
        response=GET_EMPTY_PORTS_RESPONSE,
        device=io_port_management,
    )

    await io_port_management.update()
    assert io_port_management.initialized
    assert len(io_port_management.values()) == 0


async def test_set_ports(aiohttp_mock_server, io_port_management):
    """Test set_ports call."""
    requests: list[dict[str, object]] = []

    _server, requests = await aiohttp_mock_server(
        "/axis-cgi/io/portmanagement.cgi",
        response={"apiVersion": "1.0", "context": "Axis library"},
        device=io_port_management,
        capture_payload=True,
    )

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

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/io/portmanagement.cgi"
    assert requests[-1]["payload"] == {
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


async def test_set_state_sequence(aiohttp_mock_server, io_port_management):
    """Test setting state sequence call."""
    requests: list[dict[str, object]] = []

    _server, requests = await aiohttp_mock_server(
        "/axis-cgi/io/portmanagement.cgi",
        response={"apiVersion": "1.0", "context": "Axis library"},
        device=io_port_management,
        capture_payload=True,
    )

    await io_port_management.set_state_sequence(
        "0", [Sequence("open", 3000), Sequence("closed", 5000)]
    )

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/io/portmanagement.cgi"
    assert requests[-1]["payload"] == {
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


async def test_get_supported_versions(aiohttp_mock_server, io_port_management):
    """Test get_supported_versions."""
    requests: list[dict[str, object]] = []

    _server, requests = await aiohttp_mock_server(
        "/axis-cgi/io/portmanagement.cgi",
        response=GET_SUPPORTED_VERSIONS_RESPONSE,
        device=io_port_management,
        capture_payload=True,
    )

    response = await io_port_management.get_supported_versions()

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/io/portmanagement.cgi"
    assert requests[-1]["payload"] == {
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
