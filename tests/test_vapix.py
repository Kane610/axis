"""Test Vapix network API main class.

pytest --cov-report term-missing --cov=axis.vapix tests/test_vapix.py
"""

from unittest.mock import call
from asynctest import Mock, patch
import json
import pytest

from axis.errors import Unauthorized
from axis.applications import APPLICATION_STATE_RUNNING, APPLICATION_STATE_STOPPED
from axis.stream_profiles import StreamProfile
from axis.vapix import Vapix

from .test_api_discovery import response_getApiList as api_discovery_response
from .test_applications import list_applications_response as applications_response
from .test_basic_device_info import (
    response_getAllProperties as basic_device_info_response,
)
from .test_light_control import response_getLightInformation as light_control_response
from .test_motion_guard import response_get_configuration as motion_guard_response
from .test_port_management import response_getPorts as io_port_management_response
from .test_param_cgi import response_param_cgi
from .test_stream_profiles import response_list as stream_profiles_response
from .test_vmd4 import response_get_configuration as vmd4_response


@pytest.fixture
def mock_config() -> Mock:
    """Returns the configuration mock object."""
    mock_config = Mock()
    mock_config.host = "mock_host"
    mock_config.url = "mock_url"
    mock_config.session.get = "mock_get"
    mock_config.session.post = "mock_post"
    return mock_config


def test_initialize_api_discovery(mock_config):
    """Verify that you can initialize API Discovery and that devicelist parameters."""
    with patch(
        "axis.vapix.session_request",
        side_effect=[
            json.dumps(api_discovery_response),
            json.dumps(basic_device_info_response),
            json.dumps(io_port_management_response),
            json.dumps(light_control_response),
            json.dumps(stream_profiles_response),
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
                "mock_post",
                "mock_url/axis-cgi/apidiscovery.cgi",
                json={
                    "method": "getApiList",
                    "apiVersion": "1.0",
                    "context": "Axis library",
                },
            ),
            call(
                "mock_post",
                "mock_url/axis-cgi/basicdeviceinfo.cgi",
                json={
                    "method": "getAllProperties",
                    "apiVersion": "1.1",
                    "context": "Axis library",
                },
            ),
            call(
                "mock_post",
                "mock_url/axis-cgi/io/portmanagement.cgi",
                json={
                    "method": "getPorts",
                    "apiVersion": "1.0",
                    "context": "Axis library",
                },
            ),
            call(
                "mock_post",
                "mock_url/axis-cgi/lightcontrol.cgi",
                json={
                    "method": "getLightInformation",
                    "apiVersion": "1.1",
                    "context": "Axis library",
                },
            ),
            call(
                "mock_post",
                "mock_url/axis-cgi/streamprofile.cgi",
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
        "axis.vapix.session_request",
        side_effect=[response_param_cgi, json.dumps(light_control_response)],
    ) as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_param_cgi()

    mock_request.assert_has_calls(
        [
            call("mock_get", "mock_url/axis-cgi/param.cgi?action=list"),
            call(
                "mock_post",
                "mock_url/axis-cgi/lightcontrol.cgi",
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
    with patch("axis.vapix.session_request", return_value="key=value") as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_param_cgi(preload_data=False)

    mock_request.assert_not_called


def test_initialize_applications(mock_config):
    """Verify you can list and retrieve descriptions of applications."""
    with patch(
        "axis.vapix.session_request",
        side_effect=[
            response_param_cgi,
            json.dumps(light_control_response),
            applications_response,
            json.dumps(vmd4_response),
            json.dumps(motion_guard_response),
        ],
    ) as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_param_cgi()
        vapix.initialize_applications()

    assert vapix.vmd4
    assert vapix.motion_guard

    mock_request.assert_has_calls(
        [
            call("mock_post", "mock_url/axis-cgi/applications/list.cgi"),
            call(
                "mock_post",
                "mock_url/local/vmd/control.cgi",
                json={
                    "method": "getConfiguration",
                    "apiVersion": "1.4",
                    "context": "Axis library",
                },
            ),
            call(
                "mock_post",
                "mock_url/local/motionguard/control.cgi",
                json={
                    "method": "getConfiguration",
                    "apiVersion": "1.3",
                    "context": "Axis library",
                },
            ),
        ]
    )

    assert len(vapix.applications.values()) == 5

    assert len(vapix.vmd4.values()) == 1
    assert "Camera1Profile1" in vapix.vmd4

    assert len(vapix.motion_guard.values()) == 1
    assert "Camera1Profile1" in vapix.motion_guard


def test_initialize_applications_not_running(mock_config):
    """Verify you can list and retrieve descriptions of applications."""
    with patch(
        "axis.vapix.session_request",
        side_effect=[
            response_param_cgi,
            json.dumps(light_control_response),
            applications_response.replace(
                APPLICATION_STATE_RUNNING, APPLICATION_STATE_STOPPED
            ),
        ],
    ) as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_param_cgi()
        vapix.initialize_applications()

    assert vapix.vmd4 is None
    assert vapix.motion_guard is None


def test_applications_dont_load_without_params(mock_config):
    """Verify that you can list parameters."""
    with patch("axis.vapix.session_request", return_value="key=value") as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_param_cgi(preload_data=False)
        vapix.initialize_applications()

    mock_request.assert_not_called


def test_initialize_users(mock_config):
    """Verify that you can list parameters."""
    with patch(
        "axis.vapix.session_request",
        return_value="""users="userv"
viewer="userv"
operator="usera"
admin="usera"
ptz=
""",
    ) as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_users()

    mock_request.assert_called_with(
        "mock_get", "mock_url/axis-cgi/pwdgrp.cgi?action=get"
    )
    assert vapix.users["userv"].viewer


def test_initialize_api_discovery_unauthorized(mock_config):
    """Test initialize api discovery doesnt break due to exception."""
    with patch(
        "axis.vapix.session_request",
        side_effect=[
            json.dumps(api_discovery_response),
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


# def test_initialize_param_cgi(mock_config):
#     """Test initialize api discovery doesnt break due to exception."""
#     with patch(
#         "axis.vapix.session_request",
#         side_effect=[
#             json.dumps(api_discovery_response),
#             Unauthorized,
#             Unauthorized,
#             Unauthorized,
#             Unauthorized,
#         ],
#     ):
#         vapix = Vapix(mock_config)
#         vapix.initialize_api_discovery()

#     assert vapix.basic_device_info is None
#     assert vapix.ports is None
#     assert vapix.light_control is None
#     assert vapix.mqtt is not None
#     assert vapix.stream_profiles is None
