"""Test Axis stream profiles API."""

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

from aiohttp import web
import pytest

if TYPE_CHECKING:
    from axis.device import AxisDevice
    from axis.interfaces.stream_profiles import StreamProfilesHandler


@pytest.fixture
def stream_profiles(axis_device_aiohttp: AxisDevice) -> StreamProfilesHandler:
    """Return the stream_profiles mock object."""
    axis_device_aiohttp.vapix.api_discovery = api_discovery_mock = MagicMock()
    api_discovery_mock.__getitem__().version = "1.0"
    return axis_device_aiohttp.vapix.stream_profiles


async def test_list_stream_profiles(
    aiohttp_server, stream_profiles: StreamProfilesHandler
) -> None:
    """Test get_supported_versions."""
    requests: list[dict[str, object]] = []

    async def handle_request(request: web.Request) -> web.Response:
        requests.append(
            {
                "method": request.method,
                "path": request.path,
                "payload": await request.json(),
            }
        )
        return web.json_response(LIST_RESPONSE)

    app = web.Application()
    app.router.add_post("/axis-cgi/streamprofile.cgi", handle_request)
    server = await aiohttp_server(app)
    stream_profiles.vapix.device.config.port = server.port

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
    aiohttp_server,
    stream_profiles: StreamProfilesHandler,
) -> None:
    """Test get_supported_versions."""

    async def handle_request(_: web.Request) -> web.Response:
        return web.json_response(
            {
                "method": "list",
                "apiVersion": "1.0",
                "context": "",
                "data": {
                    "maxProfiles": 0,
                },
            }
        )

    app = web.Application()
    app.router.add_post("/axis-cgi/streamprofile.cgi", handle_request)
    server = await aiohttp_server(app)
    stream_profiles.vapix.device.config.port = server.port

    await stream_profiles.update()

    assert len(stream_profiles.values()) == 0


async def test_get_supported_versions(
    aiohttp_server, stream_profiles: StreamProfilesHandler
) -> None:
    """Test get_supported_versions."""
    requests: list[dict[str, object]] = []

    async def handle_request(request: web.Request) -> web.Response:
        requests.append(
            {
                "method": request.method,
                "path": request.path,
                "payload": await request.json(),
            }
        )
        return web.json_response(GET_SUPPORTED_VERSIONS_RESPONSE)

    app = web.Application()
    app.router.add_post("/axis-cgi/streamprofile.cgi", handle_request)
    server = await aiohttp_server(app)
    stream_profiles.vapix.device.config.port = server.port

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
