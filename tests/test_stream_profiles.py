"""Test Axis stream profiles API.

pytest --cov-report term-missing --cov=axis.stream_profiles tests/test_stream_profiles.py
"""

import json

import pytest
import respx

from axis.vapix.interfaces.stream_profiles import StreamProfiles

from .conftest import HOST


@pytest.fixture
def stream_profiles(axis_device) -> StreamProfiles:
    """Return the stream_profiles mock object."""
    return StreamProfiles(axis_device.vapix)


@respx.mock
@pytest.mark.asyncio
async def test_list_stream_profiles(stream_profiles):
    """Test get_supported_versions."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/streamprofile.cgi").respond(
        json=response_list,
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

    assert len(stream_profiles.values()) == 1

    stream_profile = stream_profiles["My full HD profile"]
    assert stream_profile.id == "My full HD profile"
    assert stream_profile.name == "My full HD profile"
    assert stream_profile.description == "HD profile:1920x1080"
    assert stream_profile.parameters == "resolution=1920x1080"


@respx.mock
@pytest.mark.asyncio
async def test_list_stream_profiles_no_profiles(stream_profiles):
    """Test get_supported_versions."""
    respx.post(f"http://{HOST}:80/axis-cgi/streamprofile.cgi").respond(
        json={
            "method": "list",
            "apiVersion": "1.0",
            "data": {
                "maxProfiles": 0,
            },
        },
    )
    await stream_profiles.update()

    assert len(stream_profiles.values()) == 0


@respx.mock
@pytest.mark.asyncio
async def test_get_supported_versions(stream_profiles):
    """Test get_supported_versions."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/streamprofile.cgi").respond(
        json=response_getSupportedVersions,
    )
    response = await stream_profiles.get_supported_versions()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/streamprofile.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getSupportedVersions"
    }

    assert response["data"] == {"apiVersions": ["1.0"]}


response_list = {
    "method": "list",
    "apiVersion": "1.0",
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


response_getSupportedVersions = {
    "method": "getSupportedVersions",
    "data": {"apiVersions": ["1.0"]},
}
