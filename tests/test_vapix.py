"""Test Vapix network API main class.

pytest --cov-report term-missing --cov=axis.vapix tests/test_vapix.py
"""

import httpx
import pytest

from axis.device import AxisDevice
from axis.errors import (
    Forbidden,
    MethodNotAllowed,
    PathNotFound,
    RequestError,
    Unauthorized,
)
from axis.interfaces.vapix import Vapix
from axis.models.applications.application import ApplicationStatus
from axis.models.pwdgrp_cgi import SecondaryGroup
from axis.models.stream_profile import StreamProfile

from .applications.test_applications import (
    LIST_APPLICATIONS_RESPONSE as APPLICATIONS_RESPONSE,
)
from .applications.test_fence_guard import (
    GET_CONFIGURATION_RESPONSE as FENCE_GUARD_RESPONSE,
)
from .applications.test_loitering_guard import (
    GET_CONFIGURATION_RESPONSE as LOITERING_GUARD_RESPONSE,
)
from .applications.test_motion_guard import (
    GET_CONFIGURATION_RESPONSE as MOTION_GUARD_RESPONSE,
)
from .applications.test_vmd4 import GET_CONFIGURATION_RESPONSE as VMD4_RESPONSE
from .event_fixtures import EVENT_INSTANCES
from .parameters.test_param_cgi import PARAM_RESPONSE as PARAM_CGI_RESPONSE
from .test_api_discovery import GET_API_LIST_RESPONSE as API_DISCOVERY_RESPONSE
from .test_basic_device_info import (
    GET_ALL_PROPERTIES_RESPONSE as BASIC_DEVICE_INFO_RESPONSE,
)
from .test_light_control import GET_LIGHT_INFORMATION_RESPONSE as LIGHT_CONTROL_RESPONSE
from .test_port_management import GET_PORTS_RESPONSE as IO_PORT_MANAGEMENT_RESPONSE
from .test_stream_profiles import LIST_RESPONSE as STREAM_PROFILE_RESPONSE


@pytest.fixture
def vapix(axis_device: AxisDevice) -> Vapix:
    """Return the vapix object."""
    return axis_device.vapix


def test_vapix_not_initialized(vapix: Vapix) -> None:
    """Test Vapix class without initialising any data."""
    assert dict(vapix.basic_device_info.items()) == {}
    assert list(vapix.basic_device_info.keys()) == []
    assert list(vapix.basic_device_info.values()) == []
    assert vapix.basic_device_info.get("0") is None
    with pytest.raises(KeyError):
        assert vapix.basic_device_info["0"]
    assert iter(vapix.basic_device_info)
    assert vapix.firmware_version == ""
    assert vapix.product_number == ""
    assert vapix.product_type == ""
    assert vapix.serial_number == ""
    assert vapix.streaming_profiles == []
    assert not vapix.users.supported


async def test_initialize(respx_mock, vapix: Vapix):
    """Verify that you can initialize all APIs."""
    respx_mock.post("/axis-cgi/apidiscovery.cgi").respond(
        json=API_DISCOVERY_RESPONSE,
    )
    respx_mock.post("/axis-cgi/basicdeviceinfo.cgi").respond(
        json=BASIC_DEVICE_INFO_RESPONSE,
    )
    respx_mock.post("/axis-cgi/io/portmanagement.cgi").respond(
        json=IO_PORT_MANAGEMENT_RESPONSE,
    )
    respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json=LIGHT_CONTROL_RESPONSE,
    )
    respx_mock.post("/axis-cgi/streamprofile.cgi").respond(
        json=STREAM_PROFILE_RESPONSE,
    )
    respx_mock.post("/axis-cgi/viewarea/info.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "",
            "method": "list",
            "data": {"viewAreas": []},
        }
    )

    respx_mock.post("/axis-cgi/param.cgi").respond(text=PARAM_CGI_RESPONSE)

    respx_mock.post("/axis-cgi/applications/list.cgi").respond(
        text=APPLICATIONS_RESPONSE,
        headers={"Content-Type": "text/xml"},
    )
    respx_mock.post("/local/fenceguard/control.cgi").respond(
        json=FENCE_GUARD_RESPONSE,
    )
    respx_mock.post("/local/loiteringguard/control.cgi").respond(
        json=LOITERING_GUARD_RESPONSE,
    )
    respx_mock.post("/local/motionguard/control.cgi").respond(
        json=MOTION_GUARD_RESPONSE,
    )
    respx_mock.post("/local/vmd/control.cgi").respond(
        json=VMD4_RESPONSE,
    )

    await vapix.initialize()

    assert vapix.api_discovery.initialized
    assert vapix.basic_device_info.initialized
    assert vapix.light_control.initialized
    assert not vapix.mqtt.initialized
    assert vapix.stream_profiles.initialized
    assert vapix.view_areas.initialized

    assert vapix.firmware_version == "9.80.1"
    assert vapix.product_number == "M1065-LW"
    assert vapix.product_type == "Network Camera"
    assert vapix.serial_number == "ACCC12345678"

    assert vapix.fence_guard.initialized
    assert vapix.loitering_guard.initialized
    assert vapix.motion_guard.initialized
    assert not vapix.object_analytics.initialized
    assert vapix.vmd4.initialized


async def test_initialize_api_discovery(respx_mock, vapix: Vapix):
    """Verify that you can initialize API Discovery and that devicelist parameters."""
    respx_mock.post("/axis-cgi/apidiscovery.cgi").respond(
        json=API_DISCOVERY_RESPONSE,
    )
    respx_mock.post("/axis-cgi/basicdeviceinfo.cgi").respond(
        json=BASIC_DEVICE_INFO_RESPONSE,
    )
    respx_mock.post("/axis-cgi/io/portmanagement.cgi").respond(
        json=IO_PORT_MANAGEMENT_RESPONSE,
    )
    respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json=LIGHT_CONTROL_RESPONSE,
    )
    respx_mock.post("/axis-cgi/streamprofile.cgi").respond(
        json=STREAM_PROFILE_RESPONSE,
    )
    respx_mock.post("/axis-cgi/viewarea/info.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "",
            "method": "list",
            "data": {"viewAreas": []},
        }
    )

    await vapix.initialize_api_discovery()

    assert vapix.api_discovery
    assert vapix.basic_device_info
    assert vapix.light_control
    assert vapix.mqtt is not None
    assert vapix.stream_profiles
    assert len(vapix.view_areas) == 0

    assert vapix.firmware_version == "9.80.1"
    assert vapix.product_number == "M1065-LW"
    assert vapix.product_type == "Network Camera"
    assert vapix.serial_number == "ACCC12345678"
    assert isinstance(vapix.streaming_profiles[0], StreamProfile)

    assert len(vapix.basic_device_info) == 1
    assert len(vapix.ports) == 1
    assert len(vapix.light_control) == 1
    assert len(vapix.mqtt) == 0
    assert len(vapix.stream_profiles) == 1


async def test_initialize_api_discovery_unauthorized(respx_mock, vapix: Vapix):
    """Test initialize api discovery doesnt break due to exception."""
    respx_mock.post("/axis-cgi/apidiscovery.cgi").respond(
        json=API_DISCOVERY_RESPONSE,
    )
    respx_mock.post(
        "",
        path__in=(
            "/axis-cgi/basicdeviceinfo.cgi",
            "/axis-cgi/io/portmanagement.cgi",
            "/axis-cgi/lightcontrol.cgi",
            "/axis-cgi/mqtt/client.cgi",
            "/axis-cgi/streamprofile.cgi",
            "/axis-cgi/viewarea/info.cgi",
        ),
    ).respond(status_code=401)

    await vapix.initialize_api_discovery()

    assert len(vapix.basic_device_info) == 0
    assert len(vapix.ports) == 0
    assert vapix.ports == vapix.io_port_management
    assert vapix.light_control is not None
    assert vapix.mqtt is not None
    assert len(vapix.stream_profiles) == 0


async def test_initialize_api_discovery_unsupported(respx_mock, vapix: Vapix):
    """Test initialize api discovery doesnt break due to exception."""
    respx_mock.post("/axis-cgi/apidiscovery.cgi").side_effect = PathNotFound

    await vapix.initialize_api_discovery()

    assert len(vapix.api_discovery) == 0


async def test_initialize_param_cgi(respx_mock, vapix: Vapix):
    """Verify that you can list parameters."""
    respx_mock.post("/axis-cgi/param.cgi").respond(
        text=PARAM_CGI_RESPONSE,
        headers={"Content-Type": "text/plain"},
    )
    respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json=LIGHT_CONTROL_RESPONSE,
    )
    await vapix.initialize_param_cgi()

    assert vapix.firmware_version == "9.10.1"
    assert vapix.product_number == "M1065-LW"
    assert vapix.product_type == "Network Camera"
    assert vapix.serial_number == "ACCC12345678"
    assert len(vapix.streaming_profiles) == 2

    assert len(vapix.basic_device_info) == 0
    assert len(vapix.ports.values()) == 1
    assert len(vapix.light_control.values()) == 1
    assert len(vapix.mqtt) == 0
    assert len(vapix.stream_profiles) == 0
    assert len(vapix.params.stream_profile_handler) == 1

    assert vapix.users.supported


async def test_initialize_params_no_data(respx_mock, vapix: Vapix):
    """Verify that you can list parameters."""
    param_route = respx_mock.post(
        "/axis-cgi/param.cgi",
    ).respond(text="")
    await vapix.initialize_param_cgi(preload_data=False)

    assert param_route.call_count == 4


async def test_initialize_applications(respx_mock, vapix: Vapix):
    """Verify you can list and retrieve descriptions of applications."""
    respx_mock.post("/axis-cgi/param.cgi").respond(
        text=PARAM_CGI_RESPONSE,
        headers={"Content-Type": "text/plain"},
    )
    respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json=LIGHT_CONTROL_RESPONSE,
    )
    respx_mock.post("/axis-cgi/applications/list.cgi").respond(
        text=APPLICATIONS_RESPONSE,
        headers={"Content-Type": "text/xml"},
    )
    respx_mock.post("/local/fenceguard/control.cgi").respond(
        json=FENCE_GUARD_RESPONSE,
    )
    respx_mock.post("/local/loiteringguard/control.cgi").respond(
        json=LOITERING_GUARD_RESPONSE,
    )
    respx_mock.post("/local/motionguard/control.cgi").respond(
        json=MOTION_GUARD_RESPONSE,
    )
    respx_mock.post("/local/vmd/control.cgi").respond(
        json=VMD4_RESPONSE,
    )

    await vapix.initialize_param_cgi()
    await vapix.initialize_applications()

    assert vapix.applications
    assert len(vapix.applications.values()) == 7

    assert len(vapix.fence_guard) == 1
    assert len(vapix.loitering_guard) == 1
    assert len(vapix.motion_guard) == 1
    assert len(vapix.object_analytics) == 0
    assert len(vapix.vmd4.values()) == 1


@pytest.mark.parametrize("code", [401, 403])
async def test_initialize_applications_unauthorized(respx_mock, vapix: Vapix, code):
    """Verify initialize applications doesnt break on too low credentials."""
    respx_mock.post("/axis-cgi/param.cgi").respond(
        text=PARAM_CGI_RESPONSE,
        headers={"Content-Type": "text/plain"},
    )
    respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json=LIGHT_CONTROL_RESPONSE,
    )
    respx_mock.post("/axis-cgi/applications/list.cgi").respond(status_code=code)

    await vapix.initialize_param_cgi()
    await vapix.initialize_applications()

    assert len(vapix.applications) == 0


async def test_initialize_applications_not_running(respx_mock, vapix: Vapix):
    """Verify you can list and retrieve descriptions of applications."""
    respx_mock.post("/axis-cgi/param.cgi").respond(
        text=PARAM_CGI_RESPONSE,
        headers={"Content-Type": "text/plain"},
    )
    respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json=LIGHT_CONTROL_RESPONSE,
    )
    respx_mock.post("/axis-cgi/applications/list.cgi").respond(
        text=APPLICATIONS_RESPONSE.replace(
            ApplicationStatus.RUNNING, ApplicationStatus.STOPPED
        ),
        headers={"Content-Type": "text/xml"},
    )

    await vapix.initialize_param_cgi()
    await vapix.initialize_applications()

    assert not vapix.fence_guard.initialized
    assert not vapix.loitering_guard.initialized
    assert not vapix.motion_guard.initialized
    assert not vapix.object_analytics.initialized
    assert not vapix.vmd4.initialized


async def test_initialize_event_instances(respx_mock, vapix: Vapix):
    """Verify you can list and retrieve descriptions of applications."""
    respx_mock.post("/vapix/services").respond(
        text=EVENT_INSTANCES,
        headers={"Content-Type": "application/soap+xml; charset=utf-8"},
    )

    await vapix.initialize_event_instances()

    assert vapix.event_instances
    assert len(vapix.event_instances) == 44


async def test_applications_dont_load_without_params(respx_mock, vapix: Vapix):
    """Applications depends on param cgi to be loaded first."""
    param_route = respx_mock.post(
        "/axis-cgi/param.cgi",
    ).respond(text="key=value")

    applications_route = respx_mock.post("/axis-cgi/applications/list.cgi")

    await vapix.initialize_param_cgi(preload_data=False)
    await vapix.initialize_applications()

    assert param_route.call_count == 4
    assert not applications_route.called
    assert not vapix.object_analytics.supported


async def test_initialize_users_fails_due_to_low_credentials(respx_mock, vapix: Vapix):
    """Verify that you can list parameters."""
    respx_mock.post("/axis-cgi/pwdgrp.cgi").respond(401)
    await vapix.initialize_users()
    assert len(vapix.users.values()) == 0


async def test_load_user_groups(respx_mock, vapix: Vapix):
    """Verify that you can load user groups."""
    respx_mock.get("/axis-cgi/usergroup.cgi").respond(
        text="root\nroot admin operator ptz viewer\n",
        headers={"Content-Type": "text/plain"},
    )

    await vapix.load_user_groups()

    user = vapix.user_groups.get("0")
    assert user
    assert user.privileges == SecondaryGroup.ADMIN_PTZ
    assert user.admin
    assert user.operator
    assert user.viewer
    assert user.ptz
    assert vapix.access_rights == SecondaryGroup.ADMIN_PTZ


async def test_load_user_groups_from_pwdgrpcgi(respx_mock, vapix: Vapix):
    """Verify that you can load user groups from pwdgrp.cgi."""
    respx_mock.post("/axis-cgi/pwdgrp.cgi").respond(
        text="""users=
viewer="root"
operator="root"
admin="root"
root="root"
ptz=
""",
        headers={"Content-Type": "text/plain"},
    )
    user_group_route = respx_mock.get("/axis-cgi/usergroup.cgi").respond(
        text="root\nroot admin operator ptz viewer\n",
        headers={"Content-Type": "text/plain"},
    )

    await vapix.initialize_users()
    await vapix.load_user_groups()

    assert not user_group_route.called

    user = vapix.user_groups.get("0")
    assert user
    assert user.privileges == SecondaryGroup.ADMIN
    assert user.admin
    assert user.operator
    assert user.viewer
    assert not user.ptz
    assert vapix.access_rights == SecondaryGroup.ADMIN


async def test_load_user_groups_fails_when_not_supported(respx_mock, vapix: Vapix):
    """Verify that load user groups still initialize class even when not supported."""
    respx_mock.get("/axis-cgi/usergroup.cgi").respond(404)

    await vapix.load_user_groups()

    assert len(vapix.user_groups) == 0
    assert vapix.access_rights == SecondaryGroup.UNKNOWN


async def test_not_loading_user_groups_makes_access_rights_unknown(vapix: Vapix):
    """Verify that not loading user groups still returns a proper string."""
    assert vapix.access_rights == SecondaryGroup.UNKNOWN


@pytest.mark.parametrize(
    ("code", "error"),
    [
        (401, Unauthorized),
        (403, Forbidden),
        (404, PathNotFound),
        (405, MethodNotAllowed),
    ],
)
async def test_request_raises(respx_mock, vapix: Vapix, code, error):
    """Verify that a HTTP error raises the appropriate exception."""
    respx_mock.get("").respond(status_code=code)

    with pytest.raises(error):
        await vapix.request("get", "")


@pytest.mark.parametrize(
    "side_effect", [httpx.TimeoutException, httpx.TransportError, httpx.RequestError]
)
async def test_request_side_effects(respx_mock, vapix: Vapix, side_effect):
    """Test request side effects."""
    respx_mock.get("").side_effect = side_effect

    with pytest.raises(RequestError):
        await vapix.request("get", "")
