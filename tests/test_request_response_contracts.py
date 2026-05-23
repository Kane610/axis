"""Tests for request/response typed contract mappings."""

from typing import get_args, get_origin

import pytest

from axis.models.api import ApiRequest, ApiResponse, BytesResponse
from axis.models.api_discovery import (
    GetAllApisResponse,
    GetSupportedVersionsRequest as ApiDiscoveryGetSupportedVersionsRequest,
    GetSupportedVersionsResponse as ApiDiscoveryGetSupportedVersionsResponse,
    ListApisRequest,
)
from axis.models.applications.application import (
    ListApplicationsRequest,
    ListApplicationsResponse,
)
from axis.models.applications.fence_guard import (
    GetConfigurationRequest as FenceGuardGetConfigurationRequest,
    GetConfigurationResponse as FenceGuardGetConfigurationResponse,
)
from axis.models.applications.loitering_guard import (
    GetConfigurationRequest as LoiteringGuardGetConfigurationRequest,
    GetConfigurationResponse as LoiteringGuardGetConfigurationResponse,
)
from axis.models.applications.motion_guard import (
    GetConfigurationRequest as MotionGuardGetConfigurationRequest,
    GetConfigurationResponse as MotionGuardGetConfigurationResponse,
)
from axis.models.applications.object_analytics import (
    GetConfigurationRequest as ObjectAnalyticsGetConfigurationRequest,
    GetConfigurationResponse as ObjectAnalyticsGetConfigurationResponse,
)
from axis.models.applications.vmd4 import (
    GetConfigurationRequest as Vmd4GetConfigurationRequest,
    GetConfigurationResponse as Vmd4GetConfigurationResponse,
)
from axis.models.basic_device_info import (
    GetAllPropertiesRequest,
    GetAllPropertiesResponse,
    GetSupportedVersionsRequest as BasicDeviceInfoGetSupportedVersionsRequest,
    GetSupportedVersionsResponse as BasicDeviceInfoGetSupportedVersionsResponse,
)
from axis.models.event_instance import (
    ListEventInstancesRequest,
    ListEventInstancesResponse,
)
from axis.models.light_control import (
    GetCurrentAngleOfIlluminationRequest,
    GetCurrentAngleOfIlluminationResponse,
    GetCurrentIntensityRequest,
    GetCurrentIntensityResponse,
    GetIndividualIntensityRequest,
    GetIndividualIntensityResponse,
    GetLightInformationRequest,
    GetLightInformationResponse,
    GetLightStatusRequest,
    GetLightStatusResponse,
    GetLightSynchronizeDayNightModeRequest,
    GetLightSynchronizeDayNightModeResponse,
    GetManualAngleOfIlluminationRequest,
    GetManualAngleOfIlluminationResponse,
    GetManualIntensityRequest,
    GetManualIntensityResponse,
    GetServiceCapabilitiesRequest,
    GetServiceCapabilitiesResponse,
    GetSupportedVersionsRequest as LightControlGetSupportedVersionsRequest,
    GetSupportedVersionsResponse as LightControlGetSupportedVersionsResponse,
    GetValidAngleOfIlluminationRequest,
    GetValidAngleOfIlluminationResponse,
    GetValidIntensityRequest,
    GetValidIntensityResponse,
)
from axis.models.mqtt import (
    ActivateClientRequest,
    ConfigureClientRequest,
    ConfigureEventPublicationRequest,
    DeactivateClientRequest,
    GetClientStatusRequest,
    GetClientStatusResponse,
    GetEventPublicationConfigRequest,
    GetEventPublicationConfigResponse,
)
from axis.models.parameters.param_cgi import ParamRequest, ParamResponse
from axis.models.pir_sensor_configuration import (
    GetSensitivityRequest,
    GetSensitivityResponse,
    GetSupportedVersionsRequest as PirSensorGetSupportedVersionsRequest,
    GetSupportedVersionsResponse as PirSensorGetSupportedVersionsResponse,
    ListSensorsRequest,
    ListSensorsResponse,
)
from axis.models.port_cgi import PortActionRequest
from axis.models.port_management import (
    GetPortsRequest,
    GetPortsResponse,
    GetSupportedVersionsRequest as PortManagementGetSupportedVersionsRequest,
    GetSupportedVersionsResponse as PortManagementGetSupportedVersionsResponse,
    SetPortsRequest,
    SetStateSequenceRequest,
)
from axis.models.ptz_cgi import (
    DeviceDriverRequest,
    PtzCommandRequest,
    PtzControlRequest,
    QueryRequest,
)
from axis.models.pwdgrp_cgi import (
    CreateUserRequest,
    DeleteUserRequest,
    GetUsersRequest,
    GetUsersResponse,
    ModifyUserRequest,
)
from axis.models.stream_profile import (
    GetSupportedVersionsRequest as StreamProfileGetSupportedVersionsRequest,
    GetSupportedVersionsResponse as StreamProfileGetSupportedVersionsResponse,
    ListStreamProfilesRequest,
    ListStreamProfilesResponse,
)
from axis.models.temperature_control import GetStatusAllRequest, GetStatusAllResponse
from axis.models.user_group import GetUserGroupRequest, GetUserGroupResponse
from axis.models.view_area import (
    GetSupportedVersionsRequest as ViewAreaGetSupportedVersionsRequest,
    GetSupportedVersionsResponse as ViewAreaGetSupportedVersionsResponse,
    ListViewAreasRequest,
    ListViewAreasResponse,
    ResetGeometryRequest,
    SetGeometryRequest,
)


@pytest.mark.parametrize(
    ("request_cls", "response_cls"),
    [
        (ListApisRequest, GetAllApisResponse),
        (
            ApiDiscoveryGetSupportedVersionsRequest,
            ApiDiscoveryGetSupportedVersionsResponse,
        ),
        (GetAllPropertiesRequest, GetAllPropertiesResponse),
        (
            BasicDeviceInfoGetSupportedVersionsRequest,
            BasicDeviceInfoGetSupportedVersionsResponse,
        ),
        (ListEventInstancesRequest, ListEventInstancesResponse),
        (ListApplicationsRequest, ListApplicationsResponse),
        (FenceGuardGetConfigurationRequest, FenceGuardGetConfigurationResponse),
        (
            LoiteringGuardGetConfigurationRequest,
            LoiteringGuardGetConfigurationResponse,
        ),
        (MotionGuardGetConfigurationRequest, MotionGuardGetConfigurationResponse),
        (
            ObjectAnalyticsGetConfigurationRequest,
            ObjectAnalyticsGetConfigurationResponse,
        ),
        (Vmd4GetConfigurationRequest, Vmd4GetConfigurationResponse),
        (GetLightInformationRequest, GetLightInformationResponse),
        (GetServiceCapabilitiesRequest, GetServiceCapabilitiesResponse),
        (GetLightStatusRequest, GetLightStatusResponse),
        (GetValidIntensityRequest, GetValidIntensityResponse),
        (GetManualIntensityRequest, GetManualIntensityResponse),
        (GetIndividualIntensityRequest, GetIndividualIntensityResponse),
        (GetCurrentIntensityRequest, GetCurrentIntensityResponse),
        (
            GetValidAngleOfIlluminationRequest,
            GetValidAngleOfIlluminationResponse,
        ),
        (
            GetManualAngleOfIlluminationRequest,
            GetManualAngleOfIlluminationResponse,
        ),
        (
            GetCurrentAngleOfIlluminationRequest,
            GetCurrentAngleOfIlluminationResponse,
        ),
        (
            GetLightSynchronizeDayNightModeRequest,
            GetLightSynchronizeDayNightModeResponse,
        ),
        (
            LightControlGetSupportedVersionsRequest,
            LightControlGetSupportedVersionsResponse,
        ),
        (GetClientStatusRequest, GetClientStatusResponse),
        (GetEventPublicationConfigRequest, GetEventPublicationConfigResponse),
        (ParamRequest, ParamResponse),
        (ListSensorsRequest, ListSensorsResponse),
        (GetSensitivityRequest, GetSensitivityResponse),
        (PirSensorGetSupportedVersionsRequest, PirSensorGetSupportedVersionsResponse),
        (GetPortsRequest, GetPortsResponse),
        (
            PortManagementGetSupportedVersionsRequest,
            PortManagementGetSupportedVersionsResponse,
        ),
        (GetUsersRequest, GetUsersResponse),
        (ListStreamProfilesRequest, ListStreamProfilesResponse),
        (
            StreamProfileGetSupportedVersionsRequest,
            StreamProfileGetSupportedVersionsResponse,
        ),
        (GetStatusAllRequest, GetStatusAllResponse),
        (GetUserGroupRequest, GetUserGroupResponse),
        (ListViewAreasRequest, ListViewAreasResponse),
        (SetGeometryRequest, ListViewAreasResponse),
        (ResetGeometryRequest, ListViewAreasResponse),
        (ViewAreaGetSupportedVersionsRequest, ViewAreaGetSupportedVersionsResponse),
    ],
)
def test_request_response_type_contracts(request_cls, response_cls) -> None:
    """Verify request classes expose the intended typed response contract."""
    assert request_cls.response_type is response_cls
    generic_base = request_cls.__orig_bases__[0]
    assert get_origin(generic_base) is ApiRequest
    assert get_args(generic_base) == (response_cls,)


@pytest.mark.parametrize(
    "request_cls",
    [
        ActivateClientRequest,
        ConfigureClientRequest,
        ConfigureEventPublicationRequest,
        DeactivateClientRequest,
        PortActionRequest,
        SetPortsRequest,
        SetStateSequenceRequest,
        CreateUserRequest,
        ModifyUserRequest,
        DeleteUserRequest,
        PtzControlRequest,
        QueryRequest,
        DeviceDriverRequest,
        PtzCommandRequest,
    ],
)
def test_write_and_bytes_requests_have_no_response_contract(request_cls) -> None:
    """Verify write requests use wrapped raw-byte response contracts."""
    assert request_cls.response_type is BytesResponse
    generic_base = request_cls.__orig_bases__[0]
    assert get_origin(generic_base) is ApiRequest
    assert get_args(generic_base) == (ApiResponse[bytes],)
