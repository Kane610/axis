"""Test Vapix network API main class.

pytest --cov-report term-missing --cov=axis.vapix tests/test_vapix.py
"""

from typing import TYPE_CHECKING

import pytest

from axis.errors import (
    Forbidden,
    MethodNotAllowed,
    PathNotFound,
    RequestError,
    Unauthorized,
)
from axis.interfaces.api_handler import HandlerGroup
from axis.interfaces.event_extension_contracts import (
    DesiredEventSubscription,
    EventTransport,
)
from axis.interfaces.unique_id_migration import UNIQUE_ID_MIGRATION_VERSION
from axis.models.api_discovery import ApiId, ListApisRequest
from axis.models.applications.application import (
    ApplicationStatus,
    ListApplicationsRequest,
)
from axis.models.basic_device_info import GetAllPropertiesRequest
from axis.models.event_instance import (
    EventInstance,
    EventInstanceData,
    EventInstanceSource,
)
from axis.models.light_control import GetLightInformationRequest
from axis.models.parameters.param_cgi import ParamRequest
from axis.models.port_management import GetPortsRequest
from axis.models.pwdgrp_cgi import SecondaryGroup
from axis.models.stream_profile import ListStreamProfilesRequest, StreamProfile
from axis.models.view_area import ListViewAreasRequest

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
from .http_route_mock import (
    SimulateConnectionError,
    SimulateRequestError,
    SimulateTimeout,
)
from .parameters.test_param_cgi import PARAM_RESPONSE as PARAM_CGI_RESPONSE
from .test_api_discovery import GET_API_LIST_RESPONSE as API_DISCOVERY_RESPONSE
from .test_basic_device_info import (
    GET_ALL_PROPERTIES_RESPONSE as BASIC_DEVICE_INFO_RESPONSE,
)
from .test_light_control import GET_LIGHT_INFORMATION_RESPONSE as LIGHT_CONTROL_RESPONSE
from .test_port_management import GET_PORTS_RESPONSE as IO_PORT_MANAGEMENT_RESPONSE
from .test_stream_profiles import LIST_RESPONSE as STREAM_PROFILE_RESPONSE

from tests.conftest import MockApiResponseSpec, bind_mock_api_request

if TYPE_CHECKING:
    from axis.device import AxisDevice
    from axis.interfaces.vapix import Vapix


@pytest.fixture
async def http_route_mock(
    http_route_mock_factory,
    axis_device: AxisDevice,
    axis_companion_device: AxisDevice,
):
    """Return a two-device route mock for this module.

    This fixture intentionally overrides the default single-device
    ``http_route_mock`` fixture from conftest.py so vapix initialization tests can
    exercise companion-device behavior with a shared mock server.
    """
    return await http_route_mock_factory(
        axis_device,
        axis_companion_device,
    )


@pytest.fixture
def vapix(axis_device: AxisDevice) -> Vapix:
    """Return the vapix object."""
    return axis_device.vapix


@pytest.fixture
def vapix_companion_device(axis_companion_device: AxisDevice) -> Vapix:
    """Return the vapix object."""
    return axis_companion_device.vapix


@pytest.fixture
def mock_vapix_request(mock_api_request):
    """Register VAPIX request mocks using ApiRequest classes."""

    def _register(api_request, *, json=None, text=None, content=None, headers=None):
        return bind_mock_api_request(mock_api_request, api_request)(
            response=MockApiResponseSpec(
                json=json,
                text=text,
                content=content,
                headers=headers,
            ),
        )

    return _register


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


def test_vapix_extension_helpers(vapix: Vapix) -> None:
    """Extension helper APIs should be available without side effects."""
    capabilities = vapix.get_event_transport_capabilities()
    assert EventTransport.RTSP in capabilities
    assert EventTransport.WEBSOCKET in capabilities
    assert EventTransport.MQTT in capabilities

    assert vapix.get_supported_event_descriptors() == {}
    assert vapix.build_transport_filter_payloads(
        subscriptions=[DesiredEventSubscription(topic="onvif:Device/axis:Sensor/PIR")]
    ) == {
        "canonical_topics": ["tns1:Device/tnsaxis:Sensor/PIR"],
        "mqtt_topics": ["onvif:Device/axis:Sensor/PIR"],
        "websocket_topic_filters": ["onvif:Device/axis:Sensor/PIR"],
    }


def test_vapix_unique_id_migration_helpers(vapix: Vapix) -> None:
    """Migration helpers should provide deterministic versioned rollout data."""
    unique_ids = [
        "sensor_onvif:Device/axis:Sensor/PIR_state",
        "sensor_tns1:Device/tnsaxis:Sensor/PIR_state",
    ]

    assert vapix.get_unique_id_migration_version() == UNIQUE_ID_MIGRATION_VERSION

    plan = vapix.plan_unique_id_migration(unique_ids)
    assert plan.version == UNIQUE_ID_MIGRATION_VERSION
    assert [entry.old_unique_id for entry in plan.entries] == [
        "sensor_onvif:Device/axis:Sensor/PIR_state"
    ]
    assert [entry.new_unique_id for entry in plan.entries] == [
        "sensor_tns1:Device/tnsaxis:Sensor/PIR_state"
    ]

    assert vapix.build_unique_id_alias_map(unique_ids) == {
        "sensor_onvif:Device/axis:Sensor/PIR_state": "sensor_tns1:Device/tnsaxis:Sensor/PIR_state"
    }


async def test_plan_event_transport_filters_validates_supported_topics(
    vapix: Vapix,
) -> None:
    """Planning should reject requested topics that are not in event instances."""
    topic = "tns1:Device/tnsaxis:Sensor/PIR"
    vapix.event_instances._items = {
        topic: EventInstance(
            id=topic,
            topic=topic,
            topic_filter="onvif:Device/axis:Sensor/PIR",
            is_available=True,
            is_application_data=False,
            name="pir",
            stateful=True,
            stateless=False,
            source=EventInstanceSource(),
            data=EventInstanceData(),
        )
    }

    payloads = vapix.plan_event_transport_filters(
        subscriptions=[DesiredEventSubscription(topic="onvif:Device/axis:Sensor/PIR")]
    )
    assert payloads["canonical_topics"] == [topic]

    with pytest.raises(ValueError, match="Requested unsupported topics"):
        vapix.plan_event_transport_filters(
            subscriptions=[
                DesiredEventSubscription(topic="onvif:Device/axis:Status/SystemReady")
            ]
        )


async def test_apply_event_transport_filters_calls_transport_hooks(
    vapix: Vapix,
) -> None:
    """Apply should use websocket, mqtt, and local fallback hooks when enabled."""
    topic = "tns1:Device/tnsaxis:Sensor/PIR"
    vapix.event_instances._items = {
        topic: EventInstance(
            id=topic,
            topic=topic,
            topic_filter="onvif:Device/axis:Sensor/PIR",
            is_available=True,
            is_application_data=False,
            name="pir",
            stateful=True,
            stateless=False,
            source=EventInstanceSource(),
            data=EventInstanceData(),
        )
    }

    mqtt_calls: list[list[str]] = []

    vapix.api_discovery._items[ApiId.MQTT_CLIENT] = type(
        "_Api", (), {"version": "1.0"}
    )()

    async def _configure_event_publication(
        topics: list[str], *_args, **_kwargs
    ) -> None:
        mqtt_calls.append(topics)

    vapix.mqtt.configure_event_publication = _configure_event_publication  # type: ignore[method-assign]
    vapix.device.stream.set_event_filter_list = lambda payload: setattr(
        vapix.device.stream, "_captured_filters", payload
    )
    vapix.device.event.set_allowed_topics = lambda topics: setattr(
        vapix.device.event, "_captured_allowed_topics", topics
    )

    payloads = await vapix.apply_event_transport_filters(
        subscriptions=[DesiredEventSubscription(topic="onvif:Device/axis:Sensor/PIR")]
    )

    assert payloads["canonical_topics"] == [topic]
    assert mqtt_calls == [["onvif:Device/axis:Sensor/PIR"]]
    assert vapix.device.stream._captured_filters == [
        {"topicFilter": "onvif:Device/axis:Sensor/PIR"}
    ]
    assert vapix.device.event._captured_allowed_topics == [topic]


async def test_apply_event_transport_filters_respects_apply_flags(vapix: Vapix) -> None:
    """Apply should skip hooks when apply flags are disabled."""
    topic = "tns1:Device/tnsaxis:Sensor/PIR"
    vapix.event_instances._items = {
        topic: EventInstance(
            id=topic,
            topic=topic,
            topic_filter="onvif:Device/axis:Sensor/PIR",
            is_available=True,
            is_application_data=False,
            name="pir",
            stateful=True,
            stateless=False,
            source=EventInstanceSource(),
            data=EventInstanceData(),
        )
    }

    mqtt_calls: list[list[str]] = []
    vapix.api_discovery._items[ApiId.MQTT_CLIENT] = type(
        "_Api", (), {"version": "1.0"}
    )()

    async def _configure_event_publication(
        topics: list[str], *_args, **_kwargs
    ) -> None:
        mqtt_calls.append(topics)

    vapix.mqtt.configure_event_publication = _configure_event_publication  # type: ignore[method-assign]

    payloads = await vapix.apply_event_transport_filters(
        subscriptions=[DesiredEventSubscription(topic="onvif:Device/axis:Sensor/PIR")],
        apply_mqtt=False,
        apply_websocket=False,
        apply_local_fallback=False,
    )

    assert payloads["canonical_topics"] == [topic]
    assert mqtt_calls == []


async def test_apply_event_transport_filters_skips_unsupported_mqtt(
    vapix: Vapix,
) -> None:
    """Apply should not call MQTT hook when MQTT API is unsupported."""
    topic = "tns1:Device/tnsaxis:Sensor/PIR"
    vapix.event_instances._items = {
        topic: EventInstance(
            id=topic,
            topic=topic,
            topic_filter="onvif:Device/axis:Sensor/PIR",
            is_available=True,
            is_application_data=False,
            name="pir",
            stateful=True,
            stateless=False,
            source=EventInstanceSource(),
            data=EventInstanceData(),
        )
    }

    mqtt_calls: list[list[str]] = []

    async def _configure_event_publication(
        topics: list[str], *_args, **_kwargs
    ) -> None:
        mqtt_calls.append(topics)

    vapix.mqtt.configure_event_publication = _configure_event_publication  # type: ignore[method-assign]

    payloads = await vapix.apply_event_transport_filters(
        subscriptions=[DesiredEventSubscription(topic="onvif:Device/axis:Sensor/PIR")],
        apply_websocket=False,
        apply_local_fallback=False,
    )

    assert payloads["canonical_topics"] == [topic]
    assert mqtt_calls == []


def test_api_discovery_handlers_registration(vapix: Vapix) -> None:
    """Verify grouped API-discovery handlers matches the startup contract."""
    handlers = vapix._handlers_by_group(HandlerGroup.API_DISCOVERY)

    assert handlers == (
        vapix.basic_device_info,
        vapix.io_port_management,
        vapix.light_control,
        vapix.mqtt,
        vapix.pir_sensor_configuration,
        vapix.stream_profiles,
        vapix.view_areas,
    )


def test_application_handlers_registration(vapix: Vapix) -> None:
    """Verify grouped application handlers matches the startup contract."""
    handlers = vapix._handlers_by_group(HandlerGroup.APPLICATION)

    assert handlers == (
        vapix.fence_guard,
        vapix.loitering_guard,
        vapix.motion_guard,
        vapix.object_analytics,
        vapix.vmd4,
    )


def test_param_fallback_handlers_registration(vapix: Vapix) -> None:
    """Verify grouped param.cgi fallback handlers matches startup contract."""
    handlers = vapix._handlers_by_group(HandlerGroup.PARAM_CGI_FALLBACK)

    assert handlers == (vapix.light_control,)


def test_register_handler_is_idempotent(vapix: Vapix) -> None:
    """Verify duplicate registration does not change group membership."""
    before = vapix._handlers_by_group(HandlerGroup.API_DISCOVERY)

    vapix._register_handler(vapix.basic_device_info)

    assert vapix._handlers_by_group(HandlerGroup.API_DISCOVERY) == before


def test_grouped_handlers_order_is_stable(vapix: Vapix) -> None:
    """Verify grouped handlers preserve deterministic Vapix.__init__ order."""
    first = vapix._handlers_by_group(HandlerGroup.API_DISCOVERY)
    second = vapix._handlers_by_group(HandlerGroup.API_DISCOVERY)

    assert first == second


def test_unassigned_handlers_excluded_from_grouping(vapix: Vapix) -> None:
    """Verify handlers without matching group are not returned."""
    api_handlers = vapix._handlers_by_group(HandlerGroup.API_DISCOVERY)
    app_handlers = vapix._handlers_by_group(HandlerGroup.APPLICATION)
    param_fallback_handlers = vapix._handlers_by_group(HandlerGroup.PARAM_CGI_FALLBACK)

    assert vapix.api_discovery not in api_handlers
    assert vapix.params not in api_handlers
    assert vapix.event_instances not in api_handlers

    assert vapix.api_discovery not in app_handlers
    assert vapix.params not in app_handlers
    assert vapix.event_instances not in app_handlers

    assert vapix.api_discovery not in param_fallback_handlers
    assert vapix.params not in param_fallback_handlers
    assert vapix.event_instances not in param_fallback_handlers


async def test_initialize(http_route_mock, mock_vapix_request, vapix: Vapix):
    """Verify that you can initialize all APIs."""
    mock_vapix_request(
        ListApisRequest,
        json=API_DISCOVERY_RESPONSE,
    )
    mock_vapix_request(
        GetAllPropertiesRequest,
        json=BASIC_DEVICE_INFO_RESPONSE,
    )
    mock_vapix_request(
        GetPortsRequest,
        json=IO_PORT_MANAGEMENT_RESPONSE,
    )
    mock_vapix_request(
        GetLightInformationRequest,
        json=LIGHT_CONTROL_RESPONSE,
    )
    mock_vapix_request(
        ListStreamProfilesRequest,
        json=STREAM_PROFILE_RESPONSE,
    )
    mock_vapix_request(
        ListViewAreasRequest,
        json={
            "apiVersion": "1.0",
            "context": "",
            "method": "list",
            "data": {"viewAreas": []},
        },
    )

    mock_vapix_request(
        ParamRequest,
        content=PARAM_CGI_RESPONSE.encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
    )
    mock_vapix_request(
        ListApplicationsRequest,
        text=APPLICATIONS_RESPONSE,
        headers={"Content-Type": "text/xml"},
    )
    http_route_mock.post("/local/fenceguard/control.cgi").respond(
        json=FENCE_GUARD_RESPONSE,
    )
    http_route_mock.post("/local/loiteringguard/control.cgi").respond(
        json=LOITERING_GUARD_RESPONSE,
    )
    http_route_mock.post("/local/motionguard/control.cgi").respond(
        json=MOTION_GUARD_RESPONSE,
    )
    http_route_mock.post("/local/vmd/control.cgi").respond(
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


async def test_initialize_api_discovery(mock_vapix_request, vapix: Vapix):
    """Verify that you can initialize API Discovery and that devicelist parameters."""
    mock_vapix_request(
        ListApisRequest,
        json=API_DISCOVERY_RESPONSE,
    )
    mock_vapix_request(
        GetAllPropertiesRequest,
        json=BASIC_DEVICE_INFO_RESPONSE,
    )
    mock_vapix_request(
        GetPortsRequest,
        json=IO_PORT_MANAGEMENT_RESPONSE,
    )
    mock_vapix_request(
        GetLightInformationRequest,
        json=LIGHT_CONTROL_RESPONSE,
    )
    mock_vapix_request(
        ListStreamProfilesRequest,
        json=STREAM_PROFILE_RESPONSE,
    )
    mock_vapix_request(
        ListViewAreasRequest,
        json={
            "apiVersion": "1.0",
            "context": "",
            "method": "list",
            "data": {"viewAreas": []},
        },
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


async def test_initialize_api_discovery_unauthorized(http_route_mock, vapix: Vapix):
    """Test initialize api discovery doesnt break due to exception."""
    http_route_mock.post("/axis-cgi/apidiscovery.cgi").respond(
        json=API_DISCOVERY_RESPONSE,
    )
    http_route_mock.post(
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


async def test_initialize_api_discovery_unsupported(http_route_mock, vapix: Vapix):
    """Test initialize api discovery doesnt break due to exception."""
    http_route_mock.post("/axis-cgi/apidiscovery.cgi").side_effect = PathNotFound

    await vapix.initialize_api_discovery()

    assert len(vapix.api_discovery) == 0


async def test_initialize_param_cgi(http_route_mock, mock_vapix_request, vapix: Vapix):
    """Verify that you can list parameters."""
    param_route = mock_vapix_request(
        ParamRequest,
        content=PARAM_CGI_RESPONSE.encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
    )
    light_control_route = mock_vapix_request(
        GetLightInformationRequest,
        json=LIGHT_CONTROL_RESPONSE,
    )
    await vapix.initialize_param_cgi()

    assert param_route.called
    assert light_control_route.called
    assert "Axis-Orig-Sw" not in param_route.calls.last.request.url.params
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


async def test_initialize_param_cgi_skips_fallback_when_discovery_supports_api(
    http_route_mock,
    mock_vapix_request,
    vapix: Vapix,
):
    """Verify param fallback does not run for APIs supported by discovery."""
    mock_vapix_request(
        ListApisRequest,
        json=API_DISCOVERY_RESPONSE,
    )
    mock_vapix_request(
        GetAllPropertiesRequest,
        json=BASIC_DEVICE_INFO_RESPONSE,
    )
    mock_vapix_request(
        GetPortsRequest,
        json=IO_PORT_MANAGEMENT_RESPONSE,
    )
    light_control_route = mock_vapix_request(
        GetLightInformationRequest,
        json=LIGHT_CONTROL_RESPONSE,
    )
    mock_vapix_request(
        ListStreamProfilesRequest,
        json=STREAM_PROFILE_RESPONSE,
    )
    mock_vapix_request(
        ListViewAreasRequest,
        json={
            "apiVersion": "1.0",
            "context": "",
            "method": "list",
            "data": {"viewAreas": []},
        },
    )
    mock_vapix_request(
        ParamRequest,
        content=PARAM_CGI_RESPONSE.encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
    )

    await vapix.initialize_api_discovery()
    assert light_control_route.call_count == 1

    await vapix.initialize_param_cgi()
    assert light_control_route.call_count == 1


async def test_initialize_param_cgi_for_companion_device(
    mock_vapix_request,
    vapix_companion_device: Vapix,
):
    """Verify that you can list parameters."""
    param_route = mock_vapix_request(
        ParamRequest,
        content=PARAM_CGI_RESPONSE.encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
    )
    mock_vapix_request(
        GetLightInformationRequest,
        json=LIGHT_CONTROL_RESPONSE,
    )
    await vapix_companion_device.initialize_param_cgi()

    assert param_route.called
    assert "Axis-Orig-Sw" in param_route.calls.last.request.url.params

    assert vapix_companion_device.firmware_version == "9.10.1"
    assert vapix_companion_device.product_number == "M1065-LW"
    assert vapix_companion_device.product_type == "Network Camera"
    assert vapix_companion_device.serial_number == "ACCC12345678"
    assert len(vapix_companion_device.streaming_profiles) == 2

    assert len(vapix_companion_device.basic_device_info) == 0
    assert len(vapix_companion_device.ports.values()) == 1
    assert len(vapix_companion_device.light_control.values()) == 1
    assert len(vapix_companion_device.mqtt) == 0
    assert len(vapix_companion_device.stream_profiles) == 0
    assert len(vapix_companion_device.params.stream_profile_handler) == 1

    assert vapix_companion_device.users.supported


async def test_initialize_params_no_data(http_route_mock, vapix: Vapix):
    """Verify that you can list parameters."""
    param_route = http_route_mock.post("/axis-cgi/param.cgi").respond(
        content="".encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
    )
    await vapix.initialize_param_cgi(preload_data=False)

    assert param_route.call_count == 4


async def test_initialize_applications(http_route_mock, vapix: Vapix):
    """Verify you can list and retrieve descriptions of applications."""
    http_route_mock.post("/axis-cgi/param.cgi").respond(
        content=PARAM_CGI_RESPONSE.encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
    )
    http_route_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json=LIGHT_CONTROL_RESPONSE,
    )
    http_route_mock.post("/axis-cgi/applications/list.cgi").respond(
        text=APPLICATIONS_RESPONSE,
        headers={"Content-Type": "text/xml"},
    )
    http_route_mock.post("/local/fenceguard/control.cgi").respond(
        json=FENCE_GUARD_RESPONSE,
    )
    http_route_mock.post("/local/loiteringguard/control.cgi").respond(
        json=LOITERING_GUARD_RESPONSE,
    )
    http_route_mock.post("/local/motionguard/control.cgi").respond(
        json=MOTION_GUARD_RESPONSE,
    )
    http_route_mock.post("/local/vmd/control.cgi").respond(
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
async def test_initialize_applications_unauthorized(
    http_route_mock, vapix: Vapix, code
):
    """Verify initialize applications doesnt break on too low credentials."""
    http_route_mock.post("/axis-cgi/param.cgi").respond(
        content=PARAM_CGI_RESPONSE.encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
    )
    http_route_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json=LIGHT_CONTROL_RESPONSE,
    )
    http_route_mock.post("/axis-cgi/applications/list.cgi").respond(status_code=code)

    await vapix.initialize_param_cgi()
    await vapix.initialize_applications()

    assert len(vapix.applications) == 0


async def test_initialize_applications_not_running(http_route_mock, vapix: Vapix):
    """Verify you can list and retrieve descriptions of applications."""
    http_route_mock.post("/axis-cgi/param.cgi").respond(
        content=PARAM_CGI_RESPONSE.encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
    )
    http_route_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json=LIGHT_CONTROL_RESPONSE,
    )
    http_route_mock.post("/axis-cgi/applications/list.cgi").respond(
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


async def test_initialize_event_instances(http_route_mock, vapix: Vapix):
    """Verify you can list and retrieve descriptions of applications."""
    http_route_mock.post("/vapix/services").respond(
        text=EVENT_INSTANCES,
        headers={"Content-Type": "application/soap+xml; charset=utf-8"},
    )

    await vapix.initialize_event_instances()

    assert vapix.event_instances
    assert len(vapix.event_instances) == 44
    assert "tns1:Device/tnsaxis:Sensor/PIR" in vapix.event_instances


async def test_applications_dont_load_without_params(http_route_mock, vapix: Vapix):
    """Applications depends on param cgi to be loaded first."""
    param_route = http_route_mock.post("/axis-cgi/param.cgi").respond(
        content="key=value".encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
    )
    applications_route = http_route_mock.post("/axis-cgi/applications/list.cgi")

    await vapix.initialize_param_cgi(preload_data=False)
    await vapix.initialize_applications()

    assert param_route.call_count == 4
    assert not applications_route.called
    assert not vapix.object_analytics.supported


async def test_initialize_users_fails_due_to_low_credentials(
    http_route_mock, vapix: Vapix
):
    """Verify that you can list parameters."""
    http_route_mock.post("/axis-cgi/pwdgrp.cgi").respond(401)
    await vapix.initialize_users()
    assert len(vapix.users.values()) == 0


async def test_load_user_groups(http_route_mock, vapix: Vapix):
    """Verify that you can load user groups."""
    http_route_mock.get("/axis-cgi/usergroup.cgi").respond(
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


async def test_load_user_groups_from_pwdgrpcgi(http_route_mock, vapix: Vapix):
    """Verify that you can load user groups from pwdgrp.cgi."""
    http_route_mock.post("/axis-cgi/pwdgrp.cgi").respond(
        text="""users=
viewer="root"
operator="root"
admin="root"
root="root"
ptz=
""",
        headers={"Content-Type": "text/plain"},
    )
    user_group_route = http_route_mock.get("/axis-cgi/usergroup.cgi").respond(
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


async def test_load_user_groups_fails_when_not_supported(http_route_mock, vapix: Vapix):
    """Verify that load user groups still initialize class even when not supported."""
    http_route_mock.get("/axis-cgi/usergroup.cgi").respond(404)

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
async def test_request_raises(http_route_mock, vapix: Vapix, code, error):
    """Verify that a HTTP error raises the appropriate exception."""
    http_route_mock.get("").respond(status_code=code)

    with pytest.raises(error):
        await vapix.request("get", "")


@pytest.mark.parametrize(
    "side_effect", [SimulateTimeout, SimulateConnectionError, SimulateRequestError]
)
async def test_request_side_effects(http_route_mock, vapix: Vapix, side_effect):
    """Test request side effects."""
    http_route_mock.get("").side_effect = side_effect

    with pytest.raises(RequestError):
        await vapix.request("get", "")
