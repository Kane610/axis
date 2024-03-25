"""Test Axis stream profiles API."""

import json
from unittest.mock import MagicMock

import pytest

from axis.device import AxisDevice
from axis.interfaces.stream_profiles import StreamProfilesHandler


@pytest.fixture
def stream_profiles(axis_device: AxisDevice) -> StreamProfilesHandler:
    """Return the stream_profiles mock object."""
    axis_device.vapix.api_discovery = api_discovery_mock = MagicMock()
    api_discovery_mock.__getitem__().version = "1.0"
    return axis_device.vapix.stream_profiles


async def test_list_stream_profiles(
    respx_mock, stream_profiles: StreamProfilesHandler
) -> None:
    """Test get_supported_versions."""
    route = respx_mock.post("/axis-cgi/streamprofile.cgi").respond(
        json=LIST_RESPONSE,
    )
    await stream_profiles.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/streamprofile.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "list",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"streamProfileName": []},
    }

    assert stream_profiles.initialized
    assert len(stream_profiles.values()) == 1

    stream_profile = stream_profiles["My full HD profile"]
    assert stream_profile.id == "My full HD profile"
    assert stream_profile.name == "My full HD profile"
    assert stream_profile.description == "HD profile:1920x1080"
    assert stream_profile.parameters == "resolution=1920x1080"


async def test_list_stream_profiles_no_profiles(
    respx_mock,
    stream_profiles: StreamProfilesHandler,
) -> None:
    """Test get_supported_versions."""
    respx_mock.post("/axis-cgi/streamprofile.cgi").respond(
        json={
            "method": "list",
            "apiVersion": "1.0",
            "context": "",
            "data": {
                "maxProfiles": 0,
            },
        },
    )
    await stream_profiles.update()

    assert len(stream_profiles.values()) == 0


async def test_get_supported_versions(
    respx_mock, stream_profiles: StreamProfilesHandler
) -> None:
    """Test get_supported_versions."""
    route = respx_mock.post("/axis-cgi/streamprofile.cgi").respond(
        json=GET_SUPPORTED_VERSIONS_RESPONSE,
    )
    response = await stream_profiles.get_supported_versions()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/streamprofile.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "context": "Axis library",
        "method": "getSupportedVersions",
    }

    assert response == ["1.0"]


LIST_RESPONSE = {
    "method": "list",
    "apiVersion": "1.0",
    "context": "",
    "data": {
        "streamProfile": [
            {
                "name": "My full HD profile",
                "description": "HD profile:1920x1080",
                "parameters": "resolution=1920x1080",
            }
        ],
        "maxProfiles": 26,
    },
}


GET_SUPPORTED_VERSIONS_RESPONSE = {
    "apiVersion": "1.0",
    "context": "Axis library",
    "method": "getSupportedVersions",
    "data": {"apiVersions": ["1.0"]},
}
