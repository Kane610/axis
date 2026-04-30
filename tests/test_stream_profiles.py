"""Test Axis stream profiles API."""

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

if TYPE_CHECKING:
    from axis.device import AxisDevice
    from axis.interfaces.stream_profiles import StreamProfilesHandler


@pytest.fixture
def stream_profiles(axis_device: AxisDevice) -> StreamProfilesHandler:
    """Return the stream_profiles mock object."""
    axis_device.vapix.api_discovery = api_discovery_mock = MagicMock()
    api_discovery_mock.__getitem__().version = "1.0"
    return axis_device.vapix.stream_profiles


async def test_list_stream_profiles(
    aiohttp_mock_server, stream_profiles: StreamProfilesHandler
) -> None:
    """Test get_supported_versions."""
    _server, requests = await aiohttp_mock_server(
        "/axis-cgi/streamprofile.cgi",
        response=LIST_RESPONSE,
        device=stream_profiles,
        capture_payload=True,
    )

    await stream_profiles.update()

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/streamprofile.cgi"
    assert requests[-1]["payload"] == {
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
    aiohttp_mock_server,
    stream_profiles: StreamProfilesHandler,
) -> None:
    """Test get_supported_versions."""
    _server, _requests = await aiohttp_mock_server(
        "/axis-cgi/streamprofile.cgi",
        response={
            "method": "list",
            "apiVersion": "1.0",
            "context": "",
            "data": {
                "maxProfiles": 0,
            },
        },
        device=stream_profiles,
    )

    await stream_profiles.update()

    assert len(stream_profiles.values()) == 0


async def test_get_supported_versions(
    aiohttp_mock_server, stream_profiles: StreamProfilesHandler
) -> None:
    """Test get_supported_versions."""
    _server, requests = await aiohttp_mock_server(
        "/axis-cgi/streamprofile.cgi",
        response=GET_SUPPORTED_VERSIONS_RESPONSE,
        device=stream_profiles,
        capture_payload=True,
    )

    response = await stream_profiles.get_supported_versions()

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/streamprofile.cgi"
    assert requests[-1]["payload"] == {
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
