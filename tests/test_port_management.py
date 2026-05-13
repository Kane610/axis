"""Test Axis I/O port management API.

pytest --cov-report term-missing --cov=axis.port_management tests/test_port_management.py
"""

import pytest

from axis.interfaces.port_management import IoPortManagement
from axis.models.port_management import (
    GetPortsRequest,
    GetSupportedVersionsRequest,
    PortConfiguration,
    Sequence,
    SetPortsRequest,
    SetStateSequenceRequest,
)

from tests.conftest import (
    MockApiRequestAssertions,
    MockApiResponseSpec,
    bind_mock_api_request,
)


@pytest.fixture
def io_port_management(axis_device) -> IoPortManagement:
    """Return the io_port_management mock object."""
    return IoPortManagement(axis_device.vapix)


@pytest.fixture
def mock_port_management_request(mock_api_request):
    """Register port-management route mocks via ApiRequest classes."""

    def _register(api_request, json_data, *, content=None):
        kwargs = {"response": MockApiResponseSpec(json=json_data)}
        if content is not None:
            kwargs["assertions"] = MockApiRequestAssertions(content=content)
        return bind_mock_api_request(mock_api_request, api_request)(**kwargs)

    return _register


async def test_get_ports(mock_port_management_request, io_port_management):
    """Test get_ports call."""
    route = mock_port_management_request(
        GetPortsRequest,
        GET_PORTS_RESPONSE,
        content=None,
    )

    await io_port_management.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/io/portmanagement.cgi"
    assert route.calls[0].request.content == GetPortsRequest(api_version="1.0").content

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

    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/io/portmanagement.cgi"
    assert (
        route.calls[1].request.content
        == SetPortsRequest(
            port_config=PortConfiguration("0", state="open"),
            api_version="1.0",
        ).content
    )

    await io_port_management.close("0")

    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/io/portmanagement.cgi"
    assert (
        route.calls[2].request.content
        == SetPortsRequest(
            port_config=PortConfiguration("0", state="closed"),
            api_version="1.0",
        ).content
    )


async def test_get_empty_ports_response(
    mock_port_management_request, io_port_management
):
    """Test get_ports call."""
    mock_port_management_request(
        GetPortsRequest,
        GET_EMPTY_PORTS_RESPONSE,
        content=GetPortsRequest(api_version="1.0").content,
    )

    await io_port_management.update()
    assert io_port_management.initialized
    assert len(io_port_management.values()) == 0


async def test_set_ports(mock_port_management_request, io_port_management):
    """Test set_ports call."""
    port_configuration = PortConfiguration(
        "0",
        usage="",
        direction="",
        name="",
        normal_state="",
        state="closed",
    )
    expected_request = SetPortsRequest(
        port_config=port_configuration,
        api_version="1.0",
    )
    route = mock_port_management_request(
        SetPortsRequest,
        {"apiVersion": "1.0", "context": "Axis library"},
        content=expected_request.content,
    )

    await io_port_management.set_ports([port_configuration])

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/io/portmanagement.cgi"


async def test_set_state_sequence(mock_port_management_request, io_port_management):
    """Test setting state sequence call."""
    expected_sequence = [Sequence("open", 3000), Sequence("closed", 5000)]
    route = mock_port_management_request(
        SetStateSequenceRequest,
        {"apiVersion": "1.0", "context": "Axis library"},
        content=SetStateSequenceRequest(
            port="0",
            sequence=expected_sequence,
            api_version="1.0",
        ).content,
    )

    await io_port_management.set_state_sequence("0", expected_sequence)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/io/portmanagement.cgi"


async def test_get_supported_versions(mock_port_management_request, io_port_management):
    """Test get_supported_versions."""
    route = mock_port_management_request(
        GetSupportedVersionsRequest,
        GET_SUPPORTED_VERSIONS_RESPONSE,
        content=GetSupportedVersionsRequest().content,
    )

    response = await io_port_management.get_supported_versions()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/io/portmanagement.cgi"
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
