"""Test Axis stream profiles API."""

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from axis.models.stream_profile import (
    GetSupportedVersionsRequest,
    ListStreamProfilesRequest,
)

from tests.conftest import (
    MockApiRequestAssertions,
    MockApiResponseSpec,
    bind_mock_api_request,
)

if TYPE_CHECKING:
    from axis.device import AxisDevice
    from axis.interfaces.stream_profiles import StreamProfilesHandler


@pytest.fixture
def stream_profiles(axis_device: AxisDevice) -> StreamProfilesHandler:
    """Return the stream_profiles mock object."""
    axis_device.vapix.api_discovery = api_discovery_mock = MagicMock()
    api_discovery_mock.__getitem__().version = "1.0"
    return axis_device.vapix.stream_profiles


@pytest.fixture
def mock_stream_profile_request(mock_api_request):
    """Register stream profile route mocks via ApiRequest classes."""

    def _register(api_request, json_data, *, content):
        return bind_mock_api_request(mock_api_request, api_request)(
            response=MockApiResponseSpec(json=json_data),
            assertions=MockApiRequestAssertions(content=content),
        )

    return _register


async def test_list_stream_profiles(
    mock_stream_profile_request, stream_profiles: StreamProfilesHandler
) -> None:
    """Test get_supported_versions."""
    route = mock_stream_profile_request(
        ListStreamProfilesRequest,
        LIST_RESPONSE,
        content=ListStreamProfilesRequest(api_version="1.0").content,
    )

    await stream_profiles.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/streamprofile.cgi"

    assert stream_profiles.initialized
    assert len(stream_profiles.values()) == 1

    stream_profile = stream_profiles["My full HD profile"]
    assert stream_profile.id == "My full HD profile"
    assert stream_profile.name == "My full HD profile"
    assert stream_profile.description == "HD profile:1920x1080"
    assert stream_profile.parameters == "resolution=1920x1080"


async def test_list_stream_profiles_no_profiles(
    mock_stream_profile_request,
    stream_profiles: StreamProfilesHandler,
) -> None:
    """Test get_supported_versions."""
    route = mock_stream_profile_request(
        ListStreamProfilesRequest,
        {
            "method": "list",
            "apiVersion": "1.0",
            "context": "",
            "data": {
                "maxProfiles": 0,
            },
        },
        content=ListStreamProfilesRequest(api_version="1.0").content,
    )

    await stream_profiles.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/streamprofile.cgi"

    assert len(stream_profiles.values()) == 0


async def test_get_supported_versions(
    mock_stream_profile_request, stream_profiles: StreamProfilesHandler
) -> None:
    """Test get_supported_versions."""
    route = mock_stream_profile_request(
        GetSupportedVersionsRequest,
        GET_SUPPORTED_VERSIONS_RESPONSE,
        content=GetSupportedVersionsRequest().content,
    )

    response = await stream_profiles.get_supported_versions()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/streamprofile.cgi"

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
