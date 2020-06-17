"""Test Axis I/O port management API.

pytest --cov-report term-missing --cov=axis.port_management tests/test_port_management.py
"""

from asynctest import Mock
import pytest

from axis.port_management import (
    IoPortManagement,
    PortSequence,
    Sequence,
    SetPort,
    API_DISCOVERY_ID,
)


@pytest.fixture
def io_port_management() -> IoPortManagement:
    """Returns the io_port_management mock object."""
    mock_request = Mock()
    mock_request.return_value = ""
    return IoPortManagement(mock_request)


def test_get_ports(io_port_management):
    """Test get_ports call."""
    io_port_management._request.return_value = response_getPorts
    io_port_management.update()
    io_port_management._request.assert_called_with(
        "post",
        "/axis-cgi/io/portmanagement.cgi",
        json={"method": "getPorts", "apiVersion": "1.0", "context": "Axis library"},
    )

    assert len(io_port_management.values()) == 1

    item = io_port_management["0"]
    assert item.id == "0"
    assert item.port == "0"
    assert item.name == "PIR sensor"
    assert item.configurable is False
    assert item.usage == ""
    assert item.direction == "input"
    assert item.state == "open"
    assert item.normalState == "open"

    item.open()
    item._request.assert_called_with(
        "post",
        "/axis-cgi/io/portmanagement.cgi",
        json={
            "method": "setPorts",
            "apiVersion": "1.0",
            "context": "Axis library",
            "params": [{"port": "0", "state": "open"}],
        },
    )

    item.close()
    item._request.assert_called_with(
        "post",
        "/axis-cgi/io/portmanagement.cgi",
        json={
            "method": "setPorts",
            "apiVersion": "1.0",
            "context": "Axis library",
            "params": [{"port": "0", "state": "closed"}],
        },
    )


def test_set_ports(io_port_management):
    """Test set_ports call."""
    io_port_management.set_ports([SetPort("0", state="closed")])
    io_port_management._request.assert_called_with(
        "post",
        "/axis-cgi/io/portmanagement.cgi",
        json={
            "method": "setPorts",
            "apiVersion": "1.0",
            "context": "Axis library",
            "params": [{"port": "0", "state": "closed"}],
        },
    )


def test_state_sequence(io_port_management):
    """Test set_ports call."""
    io_port_management.set_state_sequence(
        PortSequence("0", [Sequence("open", 3000), Sequence("closed", 5000)])
    )
    io_port_management._request.assert_called_with(
        "post",
        "/axis-cgi/io/portmanagement.cgi",
        json={
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
        },
    )


def test_get_supported_versions(io_port_management):
    """Test get_supported_versions"""
    io_port_management._request.return_value = response_getSupportedVersions
    response = io_port_management.get_supported_versions()
    io_port_management._request.assert_called_with(
        "post",
        "/axis-cgi/io/portmanagement.cgi",
        json={"method": "getSupportedVersions"},
    )
    assert response["data"] == {"apiVersions": ["1.0"]}


response_getPorts = {
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

response_getSupportedVersions = {
    "method": "getSupportedVersions",
    "data": {"apiVersions": ["1.0"]},
}
