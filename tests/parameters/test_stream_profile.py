"""Test Axis stream profile parameter management."""

import pytest

from axis.device import AxisDevice
from axis.interfaces.parameters.stream_profile import (
    StreamProfileParameterHandler,
)

STREAM_PROFILE_RESPONSE = """root.StreamProfile.MaxGroups=26
root.StreamProfile.S0.Description=profile_1_description
root.StreamProfile.S0.Name=profile_1
root.StreamProfile.S0.Parameters=videocodec=h264
root.StreamProfile.S1.Description=profile_2_description
root.StreamProfile.S1.Name=profile_2
root.StreamProfile.S1.Parameters=videocodec=h265"""


@pytest.fixture
def stream_profile_handler(axis_device: AxisDevice) -> StreamProfileParameterHandler:
    """Return the param cgi mock object."""
    return axis_device.vapix.params.stream_profile_handler


async def test_stream_profile_handler(
    respx_mock,
    stream_profile_handler: StreamProfileParameterHandler,
):
    """Verify that update properties works."""
    route = respx_mock.post(
        "/axis-cgi/param.cgi",
        data={"action": "list", "group": "root.StreamProfile"},
    ).respond(
        content=STREAM_PROFILE_RESPONSE.encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
    )
    assert not stream_profile_handler.initialized

    await stream_profile_handler.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/param.cgi"

    assert stream_profile_handler.initialized
    profile_params = stream_profile_handler["0"]
    assert profile_params.max_groups == 26
    assert len(profile_params.stream_profiles) == 2
    assert profile_params.stream_profiles[0].name == "profile_1"
    assert profile_params.stream_profiles[0].description == "profile_1_description"
    assert profile_params.stream_profiles[0].parameters == "videocodec=h264"
    assert profile_params.stream_profiles[1].name == "profile_2"
    assert profile_params.stream_profiles[1].description == "profile_2_description"
    assert profile_params.stream_profiles[1].parameters == "videocodec=h265"
