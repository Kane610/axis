"""Test Vapix network API main class.

pytest --cov-report term-missing --cov=axis.vapix tests/test_vapix.py
"""

import httpx
import pytest
import respx

from axis.device import AxisDevice
from axis.errors import MethodNotAllowed, PathNotFound, RequestError, Unauthorized
from axis.vapix.models.applications.application import ApplicationStatus
from axis.vapix.models.pwdgrp_cgi import SecondaryGroup
from axis.vapix.models.stream_profile import StreamProfile
from axis.vapix.vapix import Vapix

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
from .applications.test_vmd4 import response_get_configuration as vmd4_response
from .conftest import HOST
from .event_fixtures import EVENT_INSTANCES
from .test_api_discovery import response_getApiList as api_discovery_response
from .test_basic_device_info import (
    response_getAllProperties as basic_device_info_response,
)
from .test_light_control import response_getLightInformation as light_control_response
from .test_param_cgi import response_param_cgi as param_cgi_response
from .test_port_management import response_getPorts as io_port_management_response
from .test_stream_profiles import response_list as stream_profiles_response


@pytest.fixture
def vapix(axis_device: AxisDevice) -> Vapix:
    """Return the vapix object."""
    return axis_device.vapix


@respx.mock
async def test_initialize(vapix: Vapix):
    """Verify that you can initialize all APIs."""
    respx.post(f"http://{HOST}:80/axis-cgi/apidiscovery.cgi").respond(
        json=api_discovery_response,
    )
    respx.post(f"http://{HOST}:80/axis-cgi/basicdeviceinfo.cgi").respond(
        json=basic_device_info_response,
    )
    respx.post(f"http://{HOST}:80/axis-cgi/io/portmanagement.cgi").respond(
        json=io_port_management_response,
    )
    respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json=light_control_response,
    )
    respx.post(f"http://{HOST}:80/axis-cgi/streamprofile.cgi").respond(
        json=stream_profiles_response,
    )
    respx.post(f"http://{HOST}:80/axis-cgi/viewarea/info.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "",
            "method": "list",
            "data": {"viewAreas": []},
        }
    )

    respx.get(
        f"http://{HOST}:80",
        path__startswith="/axis-cgi/param.cgi",
    ).respond(text=param_cgi_response)

    respx.post(f"http://{HOST}:80/axis-cgi/applications/list.cgi").respond(
        text=applications_response,
        headers={"Content-Type": "text/xml"},
    )
    respx.post(f"http://{HOST}:80/local/fenceguard/control.cgi").respond(
        json=fence_guard_response,
    )
    respx.post(f"http://{HOST}:80/local/loiteringguard/control.cgi").respond(
        json=loitering_guard_response,
    )
    respx.post(f"http://{HOST}:80/local/motionguard/control.cgi").respond(
        json=motion_guard_response,
    )
    respx.post(f"http://{HOST}:80/local/vmd/control.cgi").respond(
        json=vmd4_response,
    )

    await vapix.initialize()

    assert vapix.api_discovery
    assert vapix.basic_device_info
    assert vapix.light_control
    assert vapix.mqtt is not None
    assert vapix.stream_profiles
    assert len(vapix.view_areas) == 0

    assert vapix.params.brand_handler.get_params()["0"].brand == "AXIS"
    assert vapix.firmware_version == "9.80.1"
    assert vapix.product_number == "M1065-LW"
    assert vapix.product_type == "Network Camera"
    assert vapix.serial_number == "ACCC12345678"

    assert len(vapix.fence_guard) == 1
    assert len(vapix.loitering_guard) == 1
    assert vapix.motion_guard
    assert len(vapix.vmd4) == 1


@respx.mock
async def test_initialize_api_discovery(vapix: Vapix):
    """Verify that you can initialize API Discovery and that devicelist parameters."""
    respx.post(f"http://{HOST}:80/axis-cgi/apidiscovery.cgi").respond(
        json=api_discovery_response,
    )
    respx.post(f"http://{HOST}:80/axis-cgi/basicdeviceinfo.cgi").respond(
        json=basic_device_info_response,
    )
    respx.post(f"http://{HOST}:80/axis-cgi/io/portmanagement.cgi").respond(
        json=io_port_management_response,
    )
    respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json=light_control_response,
    )
    respx.post(f"http://{HOST}:80/axis-cgi/streamprofile.cgi").respond(
        json=stream_profiles_response,
    )
    respx.post(f"http://{HOST}:80/axis-cgi/viewarea/info.cgi").respond(
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


@respx.mock
async def test_initialize_api_discovery_unauthorized(vapix: Vapix):
    """Test initialize api discovery doesnt break due to exception."""
    respx.post(f"http://{HOST}:80/axis-cgi/apidiscovery.cgi").respond(
        json=api_discovery_response,
    )
    respx.post(
        f"http://{HOST}:80",
        path__in=(
            "/axis-cgi/basicdeviceinfo.cgi",
            "/axis-cgi/io/portmanagement.cgi",
            "/axis-cgi/lightcontrol.cgi",
            "/axis-cgi/mqtt/client.cgi",
            "/axis-cgi/streamprofile.cgi",
            "/axis-cgi/viewarea/info.cgi",
        ),
    ).side_effect = Unauthorized

    await vapix.initialize_api_discovery()

    assert len(vapix.basic_device_info) == 0
    assert len(vapix.ports) == 0
    assert vapix.ports == vapix.io_port_management
    assert vapix.light_control is not None
    assert vapix.mqtt is not None
    assert len(vapix.stream_profiles) == 0


@respx.mock
async def test_initialize_api_discovery_unsupported(vapix: Vapix):
    """Test initialize api discovery doesnt break due to exception."""
    respx.post(f"http://{HOST}:80/axis-cgi/apidiscovery.cgi").side_effect = PathNotFound

    await vapix.initialize_api_discovery()

    assert len(vapix.api_discovery) == 0


@respx.mock
async def test_initialize_param_cgi(vapix: Vapix):
    """Verify that you can list parameters."""
    respx.get(f"http://{HOST}:80/axis-cgi/param.cgi?action=list").respond(
        text=param_cgi_response,
        headers={"Content-Type": "text/plain"},
    )
    respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json=light_control_response,
    )
    await vapix.initialize_param_cgi()

    assert vapix.params.brand_handler.get_params()["0"].brand == "AXIS"
    assert vapix.firmware_version == "9.10.1"
    assert vapix.product_number == "M1065-LW"
    assert vapix.product_type == "Network Camera"
    assert vapix.serial_number == "ACCC12345678"

    assert len(vapix.basic_device_info) == 0
    assert len(vapix.ports.values()) == 1
    assert len(vapix.light_control.values()) == 1
    assert len(vapix.mqtt) == 0
    assert len(vapix.stream_profiles) == 0
    assert len(vapix.params.stream_profile_handler) == 1


@respx.mock
async def test_initialize_params_no_data(vapix: Vapix):
    """Verify that you can list parameters."""
    param_route = respx.get(
        f"http://{HOST}:80",
        path__startswith="/axis-cgi/param.cgi",
    ).respond(text="")
    await vapix.initialize_param_cgi(preload_data=False)

    assert param_route.call_count == 5


@respx.mock
async def test_initialize_applications(vapix: Vapix):
    """Verify you can list and retrieve descriptions of applications."""
    respx.get(f"http://{HOST}:80/axis-cgi/param.cgi?action=list").respond(
        text=param_cgi_response,
        headers={"Content-Type": "text/plain"},
    )
    respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json=light_control_response,
    )
    respx.post(f"http://{HOST}:80/axis-cgi/applications/list.cgi").respond(
        text=applications_response,
        headers={"Content-Type": "text/xml"},
    )
    respx.post(f"http://{HOST}:80/local/fenceguard/control.cgi").respond(
        json=fence_guard_response,
    )
    respx.post(f"http://{HOST}:80/local/loiteringguard/control.cgi").respond(
        json=loitering_guard_response,
    )
    respx.post(f"http://{HOST}:80/local/motionguard/control.cgi").respond(
        json=motion_guard_response,
    )
    respx.post(f"http://{HOST}:80/local/vmd/control.cgi").respond(
        json=vmd4_response,
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


@respx.mock
async def test_initialize_applications_unauthorized(vapix: Vapix):
    """Verify initialize applications doesnt break on too low credentials."""
    respx.get(f"http://{HOST}:80/axis-cgi/param.cgi?action=list").respond(
        text=param_cgi_response,
        headers={"Content-Type": "text/plain"},
    )
    respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json=light_control_response,
    )
    respx.post(
        f"http://{HOST}:80/axis-cgi/applications/list.cgi"
    ).side_effect = Unauthorized

    await vapix.initialize_param_cgi()
    await vapix.initialize_applications()

    assert len(vapix.applications) == 0


@respx.mock
async def test_initialize_applications_not_running(vapix: Vapix):
    """Verify you can list and retrieve descriptions of applications."""
    respx.get(f"http://{HOST}:80/axis-cgi/param.cgi?action=list").respond(
        text=param_cgi_response,
        headers={"Content-Type": "text/plain"},
    )
    respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json=light_control_response,
    )
    respx.post(f"http://{HOST}:80/axis-cgi/applications/list.cgi").respond(
        text=applications_response.replace(
            ApplicationStatus.RUNNING.value, ApplicationStatus.STOPPED.value
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


@respx.mock
async def test_initialize_event_instances(vapix: Vapix):
    """Verify you can list and retrieve descriptions of applications."""
    respx.post(f"http://{HOST}:80/vapix/services").respond(
        text=EVENT_INSTANCES,
        headers={"Content-Type": "application/soap+xml; charset=utf-8"},
    )

    await vapix.initialize_event_instances()

    assert vapix.event_instances
    assert len(vapix.event_instances) == 44


@respx.mock
async def test_applications_dont_load_without_params(vapix: Vapix):
    """Applications depends on param cgi to be loaded first."""
    param_route = respx.get(
        f"http://{HOST}:80",
        path__startswith="/axis-cgi/param.cgi",
    ).respond(text="key=value")

    applications_route = respx.post(f"http://{HOST}:80/axis-cgi/applications/list.cgi")

    await vapix.initialize_param_cgi(preload_data=False)
    await vapix.initialize_applications()

    assert param_route.call_count == 5
    assert not applications_route.called


@respx.mock
async def test_initialize_users(vapix: Vapix):
    """Verify that you can list parameters."""
    respx.post(f"http://{HOST}:80/axis-cgi/pwdgrp.cgi").respond(
        text="""users="usera,userv"
viewer="root,userv"
operator="root,usera"
admin="root,usera"
root="root"
ptz=
""",
        headers={"Content-Type": "text/plain"},
    )

    await vapix.initialize_users()

    assert vapix.users["root"].admin
    assert vapix.users["usera"].admin
    assert vapix.users["userv"].viewer


@respx.mock
async def test_initialize_users_fails_due_to_low_credentials(vapix: Vapix):
    """Verify that you can list parameters."""
    respx.post(f"http://{HOST}:80/axis-cgi/pwdgrp.cgi").respond(401)
    await vapix.initialize_users()


@respx.mock
async def test_load_user_groups(vapix: Vapix):
    """Verify that you can load user groups."""
    respx.get(f"http://{HOST}:80/axis-cgi/usergroup.cgi").respond(
        text="root\nroot admin operator ptz viewer\n",
        headers={"Content-Type": "text/plain"},
    )

    await vapix.load_user_groups()

    assert (user := vapix.user_groups.get("0"))
    assert user.privileges == SecondaryGroup.ADMIN_PTZ
    assert user.admin
    assert user.operator
    assert user.viewer
    assert user.ptz
    assert vapix.access_rights == SecondaryGroup.ADMIN_PTZ


@respx.mock
async def test_load_user_groups_from_pwdgrpcgi(vapix: Vapix):
    """Verify that you can load user groups from pwdgrp.cgi."""
    respx.post(f"http://{HOST}:80/axis-cgi/pwdgrp.cgi").respond(
        text="""users=
viewer="root"
operator="root"
admin="root"
root="root"
ptz=
""",
        headers={"Content-Type": "text/plain"},
    )
    user_group_route = respx.get(f"http://{HOST}:80/axis-cgi/usergroup.cgi").respond(
        text="root\nroot admin operator ptz viewer\n",
        headers={"Content-Type": "text/plain"},
    )

    await vapix.initialize_users()
    await vapix.load_user_groups()

    assert not user_group_route.called

    assert (user := vapix.user_groups.get("0"))
    assert user.privileges == SecondaryGroup.ADMIN
    assert user.admin
    assert user.operator
    assert user.viewer
    assert not user.ptz
    assert vapix.access_rights == SecondaryGroup.ADMIN


@respx.mock
async def test_load_user_groups_fails_when_not_supported(vapix: Vapix):
    """Verify that load user groups still initialize class even when not supported."""
    respx.get(f"http://{HOST}:80/axis-cgi/usergroup.cgi").respond(404)

    await vapix.load_user_groups()

    assert len(vapix.user_groups) == 0
    assert vapix.access_rights == SecondaryGroup.UNKNOWN


async def test_not_loading_user_groups_makes_access_rights_unknown(vapix: Vapix):
    """Verify that not loading user groups still returns a proper string."""
    assert vapix.access_rights == SecondaryGroup.UNKNOWN


@respx.mock
@pytest.mark.parametrize(
    ("code", "error"),
    ((401, Unauthorized), (404, PathNotFound), (405, MethodNotAllowed)),
)
async def test_request_raises(vapix: Vapix, code, error):
    """Verify that a HTTP error raises the appropriate exception."""
    respx.get(f"http://{HOST}:80").respond(code)

    with pytest.raises(error):
        await vapix.request("get", "")


@respx.mock
@pytest.mark.parametrize(
    "side_effect", (httpx.TimeoutException, httpx.TransportError, httpx.RequestError)
)
async def test_request_side_effects(vapix: Vapix, side_effect):
    """Test request side effects."""
    respx.get(f"http://{HOST}:80").side_effect = side_effect

    with pytest.raises(RequestError):
        await vapix.request("get", "")
