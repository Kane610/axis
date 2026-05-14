"""Test Axis event instance API.

pytest --cov-report term-missing --cov=axis.event_instances tests/test_event_instances.py
"""

from typing import TYPE_CHECKING

import pytest

from axis.interfaces.events.event_extension_contracts import DesiredEventSubscription
from axis.models.event import Event
from axis.models.event_instance import (
    EventInstance,
    EventInstanceData,
    EventInstanceSimpleItem,
    EventInstanceSource,
    get_events,
)

from .event_fixtures import (
    EVENT_INSTANCE_PIR_SENSOR,
    EVENT_INSTANCE_STORAGE_ALERT,
    EVENT_INSTANCE_VMD4_PROFILE1,
    EVENT_INSTANCES,
    LIGHT_STATUS_INIT,
    PIR_INIT,
    VMD4_C1P1_INIT,
)

if TYPE_CHECKING:
    from axis.interfaces.event_instances import EventInstanceHandler


@pytest.fixture
def event_instances(axis_device) -> EventInstanceHandler:
    """Return the event_instances mock object."""
    return axis_device.vapix.event_instances


async def test_full_list_of_event_instances(http_route_mock, event_instances):
    """Test loading of event instances work."""
    http_route_mock.post("/vapix/services").respond(
        text=EVENT_INSTANCES,
        headers={"Content-Type": "application/soap+xml; charset=utf-8"},
    )

    await event_instances.update()

    assert len(event_instances) == 44


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        (
            EVENT_INSTANCE_PIR_SENSOR,
            {
                "topic": "tns1:Device/tnsaxis:Sensor/PIR",
                "topic_filter": "onvif:Device/axis:Sensor/PIR",
                "is_available": True,
                "is_application_data": False,
                "name": "PIR sensor",
                "message": {
                    "stateful": True,
                    "stateless": False,
                    "source": EventInstanceSource(
                        items=(
                            EventInstanceSimpleItem(
                                name="sensor",
                                nice_name="Sensor",
                                value_type="xsd:int",
                                values=("0",),
                            ),
                        )
                    ),
                    "data": EventInstanceData(
                        items=(
                            EventInstanceSimpleItem(
                                name="state",
                                nice_name="Active",
                                value_type="xsd:boolean",
                                is_property_state=True,
                            ),
                        )
                    ),
                },
            },
        ),
        (
            EVENT_INSTANCE_STORAGE_ALERT,
            {
                "topic": "tnsaxis:Storage/Alert",
                "topic_filter": "axis:Storage/Alert",
                "is_available": True,
                "is_application_data": False,
                "name": "Storage alert",
                "message": {
                    "stateful": True,
                    "stateless": False,
                    "source": EventInstanceSource(
                        items=(
                            EventInstanceSimpleItem(
                                name="disk_id",
                                nice_name="Disk",
                                value_type="xsd:string",
                                values=("SD_DISK", "NetworkShare"),
                            ),
                        )
                    ),
                    "data": EventInstanceData(
                        items=(
                            EventInstanceSimpleItem(
                                name="temperature",
                                nice_name="Temperature",
                                value_type="xsd:int",
                            ),
                            EventInstanceSimpleItem(
                                name="alert",
                                nice_name="Alert",
                                value_type="xsd:boolean",
                                is_property_state=True,
                            ),
                            EventInstanceSimpleItem(
                                name="wear",
                                nice_name="Wear",
                                value_type="xsd:int",
                            ),
                            EventInstanceSimpleItem(
                                name="overall_health",
                                nice_name="Overall Health",
                                value_type="xsd:int",
                            ),
                        )
                    ),
                },
            },
        ),
        (
            EVENT_INSTANCE_VMD4_PROFILE1,
            {
                "topic": "tnsaxis:CameraApplicationPlatform/VMD/Camera1Profile1",
                "topic_filter": "axis:CameraApplicationPlatform/VMD/Camera1Profile1",
                "is_available": True,
                "is_application_data": False,
                "name": "VMD 4: VMD 4 ACAP",
                "message": {
                    "stateful": True,
                    "stateless": False,
                    "source": EventInstanceSource(),
                    "data": EventInstanceData(
                        items=(
                            EventInstanceSimpleItem(
                                name="active",
                                value_type="xsd:boolean",
                                is_property_state=True,
                            ),
                        )
                    ),
                },
            },
        ),
    ],
)
async def test_single_event_instance(
    http_route_mock,
    event_instances: EventInstanceHandler,
    response: str,
    expected: dict,
):
    """Verify expected outcome from different event instances."""
    http_route_mock.post("/vapix/services").respond(
        text=response,
        headers={"Content-Type": "application/soap+xml; charset=utf-8"},
    )

    await event_instances.update()

    assert not event_instances.supported
    assert len(event_instances) == 1

    event = event_instances[expected["topic"]]
    assert event.id == expected["topic"]
    assert event.topic == expected["topic"]
    assert event.topic_filter == expected["topic_filter"]
    assert event.is_available == expected["is_available"]
    assert event.is_application_data == expected["is_application_data"]
    assert event.name == expected["name"]
    assert event.stateful == expected["message"]["stateful"]
    assert event.stateless == expected["message"]["stateless"]
    assert event.source == expected["message"]["source"]
    assert event.data == expected["message"]["data"]
    assert event.raw_source == expected["message"]["source"].as_raw()
    assert event.raw_data == expected["message"]["data"].as_raw()


@pytest.mark.parametrize(
    ("input", "output"),
    [
        (
            {
                "tns1:Device": {
                    "@NiceName": "Device",
                    "tnsaxis:Sensor": {
                        "@NiceName": "Device sensors",
                        "PIR": {
                            "@topic": "true",
                            "@NiceName": "PIR sensor",
                            "MessageInstance": {
                                "@isProperty": "true",
                                "SourceInstance": {
                                    "SimpleItemInstance": {
                                        "@NiceName": "Sensor",
                                        "@Type": "xsd:int",
                                        "@Name": "sensor",
                                        "Value": "0",
                                    }
                                },
                                "DataInstance": {
                                    "SimpleItemInstance": {
                                        "@NiceName": "Active",
                                        "@Type": "xsd:boolean",
                                        "@Name": "state",
                                        "@isPropertyState": "true",
                                    }
                                },
                            },
                        },
                    },
                }
            },
            [
                {
                    "topic": "tns1:Device/tnsaxis:Sensor/PIR",
                    "data": {
                        "@topic": "true",
                        "@NiceName": "PIR sensor",
                        "MessageInstance": {
                            "@isProperty": "true",
                            "SourceInstance": {
                                "SimpleItemInstance": {
                                    "@NiceName": "Sensor",
                                    "@Type": "xsd:int",
                                    "@Name": "sensor",
                                    "Value": "0",
                                }
                            },
                            "DataInstance": {
                                "SimpleItemInstance": {
                                    "@NiceName": "Active",
                                    "@Type": "xsd:boolean",
                                    "@Name": "state",
                                    "@isPropertyState": "true",
                                }
                            },
                        },
                    },
                }
            ],
        ),
        (
            {
                "tnsaxis:CameraApplicationPlatform": {
                    "VMD": {
                        "@NiceName": "Video Motion Detection",
                        "Camera1Profile1": {
                            "@topic": "true",
                            "@NiceName": "VMD 4: VMD 4 ACAP",
                            "MessageInstance": {
                                "@isProperty": "true",
                                "DataInstance": {
                                    "SimpleItemInstance": {
                                        "@Type": "xsd:boolean",
                                        "@Name": "active",
                                        "@isPropertyState": "true",
                                    }
                                },
                            },
                        },
                    }
                }
            },
            [
                {
                    "topic": "tnsaxis:CameraApplicationPlatform/VMD/Camera1Profile1",
                    "data": {
                        "@topic": "true",
                        "@NiceName": "VMD 4: VMD 4 ACAP",
                        "MessageInstance": {
                            "@isProperty": "true",
                            "DataInstance": {
                                "SimpleItemInstance": {
                                    "@Type": "xsd:boolean",
                                    "@Name": "active",
                                    "@isPropertyState": "true",
                                }
                            },
                        },
                    },
                }
            ],
        ),
    ],
)
def test_get_events(input: dict, output: list):
    """Verify expected output of get_events."""
    assert get_events(input) == output


@pytest.mark.parametrize(
    "event_stream_bytes",
    [PIR_INIT, LIGHT_STATUS_INIT, VMD4_C1P1_INIT],
)
async def test_event_instance_synthesized_event_matches_stream_content(
    http_route_mock,
    event_instances: EventInstanceHandler,
    event_stream_bytes: bytes,
) -> None:
    """Synthesize events from instances and verify stream-content parity fields."""
    http_route_mock.post("/vapix/services").respond(
        text=EVENT_INSTANCES,
        headers={"Content-Type": "application/soap+xml; charset=utf-8"},
    )

    await event_instances.update()

    expected = Event.decode(event_stream_bytes)
    per_topic = event_instances.get_expected_events_per_topic()
    actual = next(
        event
        for event in per_topic[expected.topic]
        if event.source == expected.source and event.id == expected.id
    )

    assert actual.topic == expected.topic
    assert actual.source == expected.source
    assert actual.id == expected.id
    assert actual.state == expected.state
    assert actual.operation == expected.operation
    assert actual.topic_base == expected.topic_base
    assert actual.is_tripped == expected.is_tripped


async def test_event_instance_synthesizes_unknown_topics(
    http_route_mock, event_instances
):
    """Synthesis should include topics not represented in EventTopic enum."""
    http_route_mock.post("/vapix/services").respond(
        text=EVENT_INSTANCES,
        headers={"Content-Type": "application/soap+xml; charset=utf-8"},
    )

    await event_instances.update()

    per_topic = event_instances.get_expected_events_per_topic()
    assert "tns1:Media/ProfileChanged" in per_topic
    assert (
        per_topic["tns1:Media/ProfileChanged"][0].topic == "tns1:Media/ProfileChanged"
    )


async def test_supported_event_descriptors_and_filter_payloads(
    http_route_mock, event_instances
) -> None:
    """Extension helpers should expose normalized descriptors and payloads."""
    http_route_mock.post("/vapix/services").respond(
        text=EVENT_INSTANCES,
        headers={"Content-Type": "application/soap+xml; charset=utf-8"},
    )

    await event_instances.update()

    descriptors = event_instances.get_supported_event_descriptors()
    assert "tns1:Device/tnsaxis:Sensor/PIR" in descriptors
    assert (
        descriptors["tns1:Device/tnsaxis:Sensor/PIR"]["topic_filter"]
        == "onvif:Device/axis:Sensor/PIR"
    )

    payloads = event_instances.build_transport_filter_payloads(
        subscriptions=[DesiredEventSubscription(topic="onvif:Device/axis:Sensor/PIR")]
    )
    assert payloads == {
        "canonical_topics": ["tns1:Device/tnsaxis:Sensor/PIR"],
        "mqtt_topics": ["onvif:Device/axis:Sensor/PIR"],
        "websocket_topic_filters": ["onvif:Device/axis:Sensor/PIR"],
    }


async def test_expected_events_protocol_normalization(http_route_mock, event_instances):
    """Expected-event discovery is protocol-agnostic and deterministic."""
    http_route_mock.post("/vapix/services").respond(
        text=EVENT_INSTANCES,
        headers={"Content-Type": "application/soap+xml; charset=utf-8"},
    )

    await event_instances.update()

    topics_first = set(event_instances.get_expected_events_per_topic())
    topics_second = set(event_instances.get_expected_events_per_topic())

    assert topics_first == topics_second


def test_expected_events_internal_topic_filtering(event_instances):
    """Internal-only topics are excluded by default and available on request."""
    internal_topic = "tnsaxis:CameraApplicationPlatform/VMD/xinternal_data"
    normal_topic = "tns1:Device/tnsaxis:Sensor/PIR"

    event_instances._items = {
        internal_topic: EventInstance(
            id=internal_topic,
            topic=internal_topic,
            topic_filter="axis:CameraApplicationPlatform/VMD/xinternal_data",
            is_available=True,
            is_application_data=False,
            name="internal",
            stateful=True,
            stateless=False,
            source=EventInstanceSource(),
            data=EventInstanceData(),
        ),
        normal_topic: EventInstance(
            id=normal_topic,
            topic=normal_topic,
            topic_filter="onvif:Device/axis:Sensor/PIR",
            is_available=True,
            is_application_data=False,
            name="pir",
            stateful=True,
            stateless=False,
            source=EventInstanceSource(),
            data=EventInstanceData(),
        ),
    }

    filtered = event_instances.get_expected_events_per_topic()
    unfiltered = event_instances.get_expected_events_per_topic(
        include_internal_topics=True
    )

    assert internal_topic not in filtered
    assert internal_topic in unfiltered
    assert normal_topic in filtered


@pytest.mark.parametrize(
    "raw_event",
    [
        {
            "topic": "tns1:Configuration/tnsaxis:Intercom/Changed",
            "data": {
                "@topic": "true",
                "@NiceName": "Intercom Configuration changed",
                "MessageInstance": None,
            },
        },
        {
            "topic": "tns1:Device/Trigger/Relay",
            "data": {
                "@topic": "true",
                "MessageInstance": {
                    "@isProperty": "true",
                    "SourceInstance": None,
                    "DataInstance": None,
                },
            },
        },
        {
            "topic": "tns1:Device/Trigger/Relay",
            "data": {
                "@topic": "true",
                "MessageInstance": {
                    "@isProperty": "true",
                    "SourceInstance": {
                        "SimpleItemInstance": {
                            "@Name": "RelayToken",
                            "Value": "3",
                        }
                    },
                    "DataInstance": None,
                },
            },
        },
    ],
)
def test_event_instance_decode_handles_none_shapes(raw_event: dict) -> None:
    """EventInstance.decode should normalize None-shaped nested objects safely."""
    event = EventInstance.decode(raw_event)

    assert event.topic == raw_event["topic"]
    assert isinstance(event.source, EventInstanceSource)
    assert isinstance(event.data, EventInstanceData)
    assert event.raw_source == event.source.as_raw()
    assert event.raw_data == event.data.as_raw()


def test_event_instance_source_as_raw_multiple_items() -> None:
    """Source with multiple items should keep list shape for backward compatibility."""
    source = EventInstanceSource(
        items=(
            EventInstanceSimpleItem(name="sensor", values=("0",)),
            EventInstanceSimpleItem(name="channel", values=("1",)),
        )
    )

    assert source.as_raw() == [
        {"@Name": "sensor", "Value": "0"},
        {"@Name": "channel", "Value": "1"},
    ]


async def test_event_instances_empty_message_instance_xml(
    http_route_mock, event_instances
):
    """Empty MessageInstance XML nodes should not crash event instance parsing."""
    response = """<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://www.w3.org/2003/05/soap-envelope"
    xmlns:wstop="http://docs.oasis-open.org/wsn/t-1"
    xmlns:aev="http://www.axis.com/vapix/ws/event1"
    xmlns:tns1="http://www.onvif.org/ver10/topics"
    xmlns:tnsaxis="http://www.axis.com/2009/event/topics">
  <SOAP-ENV:Body>
    <aev:GetEventInstancesResponse>
      <wstop:TopicSet>
        <tns1:Configuration>
          <tnsaxis:Intercom>
            <Changed wstop:topic="true" aev:NiceName="Intercom Configuration changed">
              <aev:MessageInstance></aev:MessageInstance>
            </Changed>
          </tnsaxis:Intercom>
        </tns1:Configuration>
      </wstop:TopicSet>
    </aev:GetEventInstancesResponse>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>
"""
    http_route_mock.post("/vapix/services").respond(
        text=response,
        headers={"Content-Type": "application/soap+xml; charset=utf-8"},
    )

    await event_instances.update()

    topic = "tns1:Configuration/tnsaxis:Intercom/Changed"
    assert topic in event_instances
    event = event_instances[topic]
    assert event.source == EventInstanceSource()
    assert event.data == EventInstanceData()
