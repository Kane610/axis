"""Test Vapix network API main class.

pytest --cov-report term-missing --cov=axis.vapix tests/test_vapix.py
"""

import json
import pytest
from unittest.mock import Mock, call, patch

from axis.errors import Unauthorized
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
from .test_param_cgi import response_param_cgi
from .test_stream_profiles import response_list as stream_profiles_response


@pytest.fixture
def mock_config() -> Mock:
    """Returns the configuration mock object."""
    config = Mock()
    config.username = "root"
    config.password = "pass"
    config.verify_ssl = False
    return config


def test_initialize_api_discovery(mock_config):
    """Verify that you can initialize API Discovery and that devicelist parameters."""
    with patch(
        "axis.vapix.Vapix.request",
        side_effect=[
            api_discovery_response,
            basic_device_info_response,
            io_port_management_response,
            light_control_response,
            stream_profiles_response,
        ],
    ) as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_api_discovery()

    assert vapix.api_discovery
    assert vapix.basic_device_info
    assert vapix.light_control
    assert vapix.mqtt
    assert vapix.stream_profiles

    assert len(mock_request.mock_calls) == 5
    mock_request.assert_has_calls(
        [
            call(
                "post",
                "/axis-cgi/apidiscovery.cgi",
                json={
                    "method": "getApiList",
                    "apiVersion": "1.0",
                    "context": "Axis library",
                },
            ),
            call(
                "post",
                "/axis-cgi/basicdeviceinfo.cgi",
                json={
                    "method": "getAllProperties",
                    "apiVersion": "1.1",
                    "context": "Axis library",
                },
            ),
            call(
                "post",
                "/axis-cgi/io/portmanagement.cgi",
                json={
                    "method": "getPorts",
                    "apiVersion": "1.0",
                    "context": "Axis library",
                },
            ),
            call(
                "post",
                "/axis-cgi/lightcontrol.cgi",
                json={
                    "method": "getLightInformation",
                    "apiVersion": "1.1",
                    "context": "Axis library",
                },
            ),
            call(
                "post",
                "/axis-cgi/streamprofile.cgi",
                json={
                    "method": "list",
                    "apiVersion": "1.0",
                    "context": "Axis library",
                    "params": {"streamProfileName": []},
                },
            ),
        ]
    )

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


def test_initialize_param_cgi(mock_config):
    """Verify that you can list parameters."""
    with patch(
        "axis.vapix.Vapix.request",
        side_effect=[response_param_cgi, light_control_response],
    ) as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_param_cgi()

    mock_request.assert_has_calls(
        [
            call("get", "/axis-cgi/param.cgi?action=list"),
            call(
                "post",
                "/axis-cgi/lightcontrol.cgi",
                json={
                    "method": "getLightInformation",
                    "apiVersion": "1.1",
                    "context": "Axis library",
                },
            ),
        ]
    )

    assert vapix.params["root.Brand.Brand"].raw == "AXIS"
    assert vapix.firmware_version == "9.10.1"
    assert vapix.product_number == "M1065-LW"
    assert vapix.product_type == "Network Camera"
    assert vapix.serial_number == "ACCC12345678"
    # assert isinstance(vapix.streaming_profiles[0], StreamProfile)

    assert vapix.basic_device_info is None
    assert len(vapix.ports.values()) == 1
    assert len(vapix.light_control.values()) == 1
    assert vapix.mqtt is None
    assert vapix.stream_profiles is None


def test_initialize_params_no_data(mock_config):
    """Verify that you can list parameters."""
    with patch("axis.vapix.Vapix.request", return_value="key=value") as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_param_cgi(preload_data=False)

    mock_request.assert_not_called


def test_initialize_applications(mock_config):
    """Verify you can list and retrieve descriptions of applications."""
    with patch(
        "axis.vapix.Vapix.request",
        side_effect=[
            response_param_cgi,
            light_control_response,
            applications_response,
            fence_guard_response,
            loitering_guard_response,
            motion_guard_response,
            vmd4_response,
        ],
    ) as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_param_cgi()
        vapix.initialize_applications()

    assert vapix.fence_guard
    assert vapix.loitering_guard
    assert vapix.motion_guard
    assert vapix.vmd4

    mock_request.assert_has_calls(
        [
            call("post", "/axis-cgi/applications/list.cgi"),
            call(
                "post",
                "/local/fenceguard/control.cgi",
                json={
                    "method": "getConfiguration",
                    "apiVersion": "1.3",
                    "context": "Axis library",
                },
            ),
            call(
                "post",
                "/local/loiteringguard/control.cgi",
                json={
                    "method": "getConfiguration",
                    "apiVersion": "1.3",
                    "context": "Axis library",
                },
            ),
            call(
                "post",
                "/local/motionguard/control.cgi",
                json={
                    "method": "getConfiguration",
                    "apiVersion": "1.3",
                    "context": "Axis library",
                },
            ),
            call(
                "post",
                "/local/vmd/control.cgi",
                json={
                    "method": "getConfiguration",
                    "apiVersion": "1.2",
                    "context": "Axis library",
                },
            ),
        ]
    )

    assert len(vapix.applications.values()) == 7

    assert len(vapix.fence_guard.values()) == 1
    assert "Camera1Profile1" in vapix.fence_guard

    assert len(vapix.loitering_guard.values()) == 1
    assert "Camera1Profile1" in vapix.loitering_guard

    assert len(vapix.motion_guard.values()) == 1
    assert "Camera1Profile1" in vapix.motion_guard

    assert len(vapix.vmd4.values()) == 1
    assert "Camera1Profile1" in vapix.vmd4


def test_initialize_applications_not_running(mock_config):
    """Verify you can list and retrieve descriptions of applications."""
    with patch(
        "axis.vapix.Vapix.request",
        side_effect=[
            response_param_cgi,
            light_control_response,
            applications_response.replace(
                APPLICATION_STATE_RUNNING, APPLICATION_STATE_STOPPED
            ),
        ],
    ):
        vapix = Vapix(mock_config)
        vapix.initialize_param_cgi()
        vapix.initialize_applications()

    assert vapix.fence_guard is None
    assert vapix.motion_guard is None
    assert vapix.vmd4 is None


def test_applications_dont_load_without_params(mock_config):
    """Verify that you can list parameters."""
    with patch("axis.vapix.Vapix.request", return_value="key=value") as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_param_cgi(preload_data=False)
        vapix.initialize_applications()

    mock_request.assert_not_called


def test_initialize_users(mock_config):
    """Verify that you can list parameters."""
    with patch(
        "axis.vapix.Vapix.request",
        return_value="""users="userv"
viewer="userv"
operator="usera"
admin="usera"
ptz=
""",
    ) as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_users()

    mock_request.assert_called_with("get", "/axis-cgi/pwdgrp.cgi?action=get")
    assert vapix.users["userv"].viewer


def test_initialize_api_discovery_unauthorized(mock_config):
    """Test initialize api discovery doesnt break due to exception."""
    with patch(
        # with patch(
        "axis.vapix.Vapix.request",
        side_effect=[
            api_discovery_response,
            Unauthorized,
            Unauthorized,
            Unauthorized,
            Unauthorized,
        ],
    ):
        vapix = Vapix(mock_config)
        vapix.initialize_api_discovery()

    assert vapix.basic_device_info is None
    assert vapix.ports is None
    assert vapix.light_control is None
    assert vapix.mqtt is not None
    assert vapix.stream_profiles is None
