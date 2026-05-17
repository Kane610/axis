"""Protocol parity tests for event-instance expected-event discovery.

pytest --cov-report term-missing --cov=axis.event_instances tests/test_event_instances_protocol_parity.py
"""

from typing import TYPE_CHECKING

import orjson
import pytest

from axis.models.event import Event
from axis.models.mqtt import mqtt_json_to_event
from axis.websocket import _parse_ws_notification

from .event_fixtures import EVENT_INSTANCES, LIGHT_STATUS_INIT, PIR_INIT, VMD4_C1P1_INIT

if TYPE_CHECKING:
    from axis.interfaces.events.event_instances import EventInstanceHandler


@pytest.fixture
def event_instances(axis_device) -> EventInstanceHandler:
    """Return event_instances handler from mocked device."""
    return axis_device.vapix.event_instances


def _mqtt_topic(topic: str) -> str:
    """Convert internal topic format to MQTT topic namespace format."""
    return topic.replace("tns1", "onvif").replace("tnsaxis", "axis")


def _event_identity(event: Event) -> tuple[str, str, str, str, str]:
    """Return identity fields used for cross-protocol parity assertions."""
    return (event.topic, event.source, event.id, event.state, event.topic_base.value)


@pytest.mark.parametrize(
    "event_stream_bytes",
    [PIR_INIT, LIGHT_STATUS_INIT, VMD4_C1P1_INIT],
)
async def test_expected_events_match_websocket_shape(
    http_route_mock,
    event_instances: EventInstanceHandler,
    event_stream_bytes: bytes,
) -> None:
    """Websocket notify payloads should align with expected-event identities."""
    http_route_mock.post("/vapix/services").respond(
        text=EVENT_INSTANCES,
        headers={"Content-Type": "application/soap+xml; charset=utf-8"},
    )

    await event_instances.update()

    expected = Event.decode(event_stream_bytes)
    notification = {
        "topic": expected.topic,
        "message": {
            "source": (
                {expected.source: expected.id}
                if expected.source and expected.id != ""
                else ({expected.source: expected.id} if expected.source else {})
            ),
            "key": {},
            "data": {expected.data.get("type", "state"): expected.state},
        },
    }

    parsed = Event.decode(_parse_ws_notification(notification))
    expected_events = event_instances.get_expected_events_per_topic()

    expected_identities = {
        _event_identity(event) for event in expected_events[expected.topic]
    }
    assert _event_identity(parsed) in expected_identities


@pytest.mark.parametrize(
    "event_stream_bytes",
    [PIR_INIT, LIGHT_STATUS_INIT, VMD4_C1P1_INIT],
)
async def test_expected_events_match_mqtt_shape(
    http_route_mock,
    event_instances: EventInstanceHandler,
    event_stream_bytes: bytes,
) -> None:
    """MQTT notify payloads should align with expected-event identities."""
    http_route_mock.post("/vapix/services").respond(
        text=EVENT_INSTANCES,
        headers={"Content-Type": "application/soap+xml; charset=utf-8"},
    )

    await event_instances.update()

    expected = Event.decode(event_stream_bytes)
    mqtt_msg = {
        "timestamp": 0,
        "topic": _mqtt_topic(expected.topic),
        "message": {
            "source": (
                {expected.source: expected.id}
                if expected.source and expected.id != ""
                else ({expected.source: expected.id} if expected.source else {})
            ),
            "key": {},
            "data": {expected.data.get("type", "state"): expected.state},
        },
    }

    parsed = Event.decode(mqtt_json_to_event(orjson.dumps(mqtt_msg)))
    expected_events = event_instances.get_expected_events_per_topic()

    expected_identities = {
        _event_identity(event) for event in expected_events[expected.topic]
    }
    assert _event_identity(parsed) in expected_identities
