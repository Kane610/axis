"""Test Vapix network API main class.

pytest --cov-report term-missing --cov=axis.vapix tests/test_vapix.py
"""

import pytest

import httpx
import respx

from axis.errors import MethodNotAllowed, PathNotFound, RequestError, Unauthorized
from axis.applications import APPLICATION_STATE_RUNNING, APPLICATION_STATE_STOPPED
from axis.stream_profiles import StreamProfile
from axis.vapix import Vapix

from .test_api_discovery import response_getApiList as api_discovery_response
from .applications.test_applications import (
    list_applications_response as applications_response,
)
from .applications.test_fence_guard import (
    response_get_configuration as fence_guard_response,
)
from .applications.test_loitering_guard import (
    response_get_configuration as loitering_guard_response,
)
from .applications.test_motion_guard import (
    response_get_configuration as motion_guard_response,
)
from .test_basic_device_info import (
    response_getAllProperties as basic_device_info_response,
)
from .applications.test_vmd4 import response_get_configuration as vmd4_response
from .test_light_control import response_getLightInformation as light_control_response
from .test_port_management import response_getPorts as io_port_management_response
from .test_param_cgi import response_param_cgi as param_cgi_response
from .test_stream_profiles import response_list as stream_profiles_response


@pytest.fixture
def vapix(axis_device) -> Vapix:
    """Return the vapix object."""
    return axis_device.vapix


@respx.mock
async def test_initialize(vapix):
    """Verify that you can initialize all APIs."""
    respx.post("http://host:80/axis-cgi/apidiscovery.cgi").respond(
        json=api_discovery_response,
    )
    respx.post("http://host:80/axis-cgi/basicdeviceinfo.cgi").respond(
        json=basic_device_info_response,
    )
    respx.post("http://host:80/axis-cgi/io/portmanagement.cgi").respond(
        json=io_port_management_response,
    )
    respx.post("http://host:80/axis-cgi/lightcontrol.cgi").respond(
        json=light_control_response,
    )
    respx.post("http://host:80/axis-cgi/streamprofile.cgi").respond(
        json=stream_profiles_response,
    )

    respx.get(
        "http://host:80",
        path__startswith="/axis-cgi/param.cgi",
    ).respond(text=param_cgi_response)

    respx.post("http://host:80/axis-cgi/applications/list.cgi").respond(
        text=applications_response,
        headers={"Content-Type": "text/xml"},
    )
    respx.post("http://host:80/local/fenceguard/control.cgi").respond(
        json=fence_guard_response,
    )
    respx.post("http://host:80/local/loiteringguard/control.cgi").respond(
        json=loitering_guard_response,
    )
    respx.post("http://host:80/local/motionguard/control.cgi").respond(
        json=motion_guard_response,
    )
    respx.post("http://host:80/local/vmd/control.cgi").respond(
        json=vmd4_response,
    )

    await vapix.initialize()

    assert vapix.api_discovery
    assert vapix.basic_device_info
    assert vapix.light_control
    assert vapix.mqtt
    assert vapix.stream_profiles

    assert vapix.params["root.Brand.Brand"] == "AXIS"
    assert vapix.firmware_version == "9.80.1"
    assert vapix.product_number == "M1065-LW"
    assert vapix.product_type == "Network Camera"
    assert vapix.serial_number == "ACCC12345678"

    assert vapix.fence_guard
    assert vapix.loitering_guard
    assert vapix.motion_guard
    assert vapix.vmd4


@respx.mock
async def test_initialize_api_discovery(vapix):
    """Verify that you can initialize API Discovery and that devicelist parameters."""
    respx.post("http://host:80/axis-cgi/apidiscovery.cgi").respond(
        json=api_discovery_response,
    )
    respx.post("http://host:80/axis-cgi/basicdeviceinfo.cgi").respond(
        json=basic_device_info_response,
    )
    respx.post("http://host:80/axis-cgi/io/portmanagement.cgi").respond(
        json=io_port_management_response,
    )
    respx.post("http://host:80/axis-cgi/lightcontrol.cgi").respond(
        json=light_control_response,
    )
    respx.post("http://host:80/axis-cgi/streamprofile.cgi").respond(
        json=stream_profiles_response,
    )

    await vapix.initialize_api_discovery()

    assert vapix.api_discovery
    assert vapix.basic_device_info
    assert vapix.light_control
    assert vapix.mqtt
    assert vapix.stream_profiles

    assert vapix.firmware_version == "9.80.1"
    assert vapix.product_number == "M1065-LW"
    assert vapix.product_type == "Network Camera"
    assert vapix.serial_number == "ACCC12345678"
    assert isinstance(vapix.streaming_profiles[0], StreamProfile)

    assert len(vapix.basic_device_info.values()) == 14
    assert len(vapix.ports.values()) == 1
    assert len(vapix.light_control.values()) == 1
    assert vapix.mqtt is not None
    assert len(vapix.stream_profiles.values()) == 1


@respx.mock
async def test_initialize_api_discovery_unauthorized(vapix):
    """Test initialize api discovery doesnt break due to exception."""
    respx.post("http://host:80/axis-cgi/apidiscovery.cgi").respond(
        json=api_discovery_response,
    )
    respx.post(
        "http://host:80",
        path__in=(
            "/axis-cgi/basicdeviceinfo.cgi",
            "/axis-cgi/io/portmanagement.cgi",
            "/axis-cgi/lightcontrol.cgi",
            "/axis-cgi/mqtt/client.cgi",
            "/axis-cgi/streamprofile.cgi",
        ),
    ).side_effect = Unauthorized

    await vapix.initialize_api_discovery()

    assert vapix.basic_device_info is None
    assert vapix.ports is None
    assert vapix.light_control is None
    assert vapix.mqtt is not None
    assert vapix.stream_profiles is None


@respx.mock
async def test_initialize_api_discovery_unsupported(vapix):
    """Test initialize api discovery doesnt break due to exception."""
    respx.post("http://host:80/axis-cgi/apidiscovery.cgi").side_effect = PathNotFound

    await vapix.initialize_api_discovery()

    assert vapix.api_discovery


@respx.mock
async def test_initialize_param_cgi(vapix):
    """Verify that you can list parameters."""
    respx.get("http://host:80/axis-cgi/param.cgi?action=list").respond(
        text=param_cgi_response,
        headers={"Content-Type": "text/plain"},
    )
    respx.post("http://host:80/axis-cgi/lightcontrol.cgi").respond(
        json=light_control_response,
    )
    await vapix.initialize_param_cgi()

    assert vapix.params["root.Brand.Brand"] == "AXIS"
    assert vapix.firmware_version == "9.10.1"
    assert vapix.product_number == "M1065-LW"
    assert vapix.product_type == "Network Camera"
    assert vapix.serial_number == "ACCC12345678"

    assert vapix.basic_device_info is None
    assert len(vapix.ports.values()) == 1
    assert len(vapix.light_control.values()) == 1
    assert vapix.mqtt is None
    assert vapix.stream_profiles is None
    assert vapix.streaming_profiles is not None


@respx.mock
async def test_initialize_params_no_data(vapix):
    """Verify that you can list parameters."""
    param_route = respx.get(
        "http://host:80",
        path__startswith="/axis-cgi/param.cgi",
    ).respond(text="key=value")
    await vapix.initialize_param_cgi(preload_data=False)

    assert param_route.call_count == 7


@respx.mock
async def test_initialize_applications(vapix):
    """Verify you can list and retrieve descriptions of applications."""
    respx.get("http://host:80/axis-cgi/param.cgi?action=list").respond(
        text=param_cgi_response,
        headers={"Content-Type": "text/plain"},
    )
    respx.post("http://host:80/axis-cgi/lightcontrol.cgi").respond(
        json=light_control_response,
    )
    respx.post("http://host:80/axis-cgi/applications/list.cgi").respond(
        text=applications_response,
        headers={"Content-Type": "text/xml"},
    )
    respx.post("http://host:80/local/fenceguard/control.cgi").respond(
        json=fence_guard_response,
    )
    respx.post("http://host:80/local/loiteringguard/control.cgi").respond(
        json=loitering_guard_response,
    )
    respx.post("http://host:80/local/motionguard/control.cgi").respond(
        json=motion_guard_response,
    )
    respx.post("http://host:80/local/vmd/control.cgi").respond(
        json=vmd4_response,
    )

    await vapix.initialize_param_cgi()
    await vapix.initialize_applications()

    assert vapix.fence_guard
    assert vapix.loitering_guard
    assert vapix.motion_guard
    assert vapix.vmd4

    assert len(vapix.applications.values()) == 7

    assert len(vapix.fence_guard.values()) == 1
    assert "Camera1Profile1" in vapix.fence_guard

    assert len(vapix.loitering_guard.values()) == 1
    assert "Camera1Profile1" in vapix.loitering_guard

    assert len(vapix.motion_guard.values()) == 1
    assert "Camera1Profile1" in vapix.motion_guard

    assert vapix.object_analytics is None

    assert len(vapix.vmd4.values()) == 1
    assert "Camera1Profile1" in vapix.vmd4


@respx.mock
async def test_initialize_applications_unauthorized(vapix):
    """Verify initialize applications doesnt break on too low credentials."""
    respx.get("http://host:80/axis-cgi/param.cgi?action=list").respond(
        text=param_cgi_response,
        headers={"Content-Type": "text/plain"},
    )
    respx.post("http://host:80/axis-cgi/lightcontrol.cgi").respond(
        json=light_control_response,
    )
    respx.post(
        "http://host:80/axis-cgi/applications/list.cgi"
    ).side_effect = Unauthorized

    await vapix.initialize_param_cgi()
    await vapix.initialize_applications()

    assert vapix.applications


@respx.mock
async def test_initialize_applications_not_running(vapix):
    """Verify you can list and retrieve descriptions of applications."""
    respx.get("http://host:80/axis-cgi/param.cgi?action=list").respond(
        text=param_cgi_response,
        headers={"Content-Type": "text/plain"},
    )
    respx.post("http://host:80/axis-cgi/lightcontrol.cgi").respond(
        json=light_control_response,
    )
    respx.post("http://host:80/axis-cgi/applications/list.cgi").respond(
        text=applications_response.replace(
            APPLICATION_STATE_RUNNING, APPLICATION_STATE_STOPPED
        ),
        headers={"Content-Type": "text/xml"},
    )

    await vapix.initialize_param_cgi()
    await vapix.initialize_applications()

    assert vapix.fence_guard is None
    assert vapix.motion_guard is None
    assert vapix.vmd4 is None


@respx.mock
async def test_applications_dont_load_without_params(vapix):
    """Applications depends on param cgi to be loaded first."""
    param_route = respx.get(
        "http://host:80",
        path__startswith="/axis-cgi/param.cgi",
    ).respond(text="key=value")

    applications_route = respx.post("http://host:80/axis-cgi/applications/list.cgi")

    await vapix.initialize_param_cgi(preload_data=False)
    await vapix.initialize_applications()

    assert param_route.call_count == 7
    assert not applications_route.called


@respx.mock
async def test_initialize_users(vapix):
    """Verify that you can list parameters."""
    respx.get("http://host:80/axis-cgi/pwdgrp.cgi?action=get").respond(
        text="""users="userv"
viewer="userv"
operator="usera"
admin="usera"
ptz=
""",
        headers={"Content-Type": "text/html"},
    )

    await vapix.initialize_users()

    assert vapix.users["userv"].viewer


@respx.mock
async def test_request_json_error(vapix):
    """Verify that a JSON error returns an empty dict."""
    respx.get("http://host:80").respond(
        json={"error": ""}, headers={"Content-Type": "application/json"}
    )

    assert await vapix.request("get", "") == {}


@respx.mock
async def test_request_plain_text_error(vapix):
    """Verify that a plain text error returns an empty string."""
    respx.get("http://host:80").respond(
        text="# Error:", headers={"Content-Type": "text/plain"}
    )

    assert await vapix.request("get", "") == ""


@respx.mock
async def test_request_401_raises_unauthorized(vapix):
    """Verify that a 401 raises Unauthorized exception.

    This typically mean that user credentials aren't high enough, e.g. viewer account.
    """
    respx.get("http://host:80").respond(401)

    with pytest.raises(Unauthorized):
        await vapix.request("get", "")


@respx.mock
async def test_request_404_raises_path_not_found(vapix):
    """Verify that a 404 raises PathNotFound exception.

    This typically means something is unsupported.
    """
    respx.get("http://host:80").respond(404)

    with pytest.raises(PathNotFound):
        await vapix.request("get", "")


@respx.mock
async def test_request_405_raises_method_not_allowed(vapix):
    """Verify that a 405 raises MethodNotAllowed exception."""
    respx.get("http://host:80").respond(405)

    with pytest.raises(MethodNotAllowed):
        await vapix.request("get", "")


@respx.mock
async def test_request_timeout(vapix):
    """Verify that you can list parameters."""
    respx.get("http://host:80").side_effect = httpx.TimeoutException

    with pytest.raises(RequestError):
        await vapix.request("get", "")


@respx.mock
async def test_request_transport_error(vapix):
    """Verify that you can list parameters."""
    respx.get("http://host:80").side_effect = httpx.TransportError

    with pytest.raises(RequestError):
        await vapix.request("get", "")


@respx.mock
async def test_request_request_error(vapix):
    """Verify that you can list parameters."""
    respx.get("http://host:80").side_effect = httpx.RequestError

    with pytest.raises(RequestError):
        await vapix.request("get", "")
