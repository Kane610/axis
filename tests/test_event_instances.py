"""Test Axis event instance API.

pytest --cov-report term-missing --cov=axis.event_instances tests/test_event_instances.py
"""

import pytest

from axis.vapix.interfaces.event_instances import EventInstanceHandler
from axis.vapix.models.event_instance import get_events

from .event_fixtures import (
    EVENT_INSTANCE_PIR_SENSOR,
    EVENT_INSTANCE_STORAGE_ALERT,
    EVENT_INSTANCE_VMD4_PROFILE1,
    EVENT_INSTANCES,
)


@pytest.fixture
def event_instances(axis_device) -> EventInstanceHandler:
    """Return the event_instances mock object."""
    return axis_device.vapix.event_instances


async def test_full_list_of_event_instances(respx_mock, event_instances):
    """Test loading of event instances work."""
    respx_mock.post("/vapix/services").respond(
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
                    "source": {
                        "@NiceName": "Sensor",
                        "@Type": "xsd:int",
                        "@Name": "sensor",
                        "Value": "0",
                    },
                    "data": {
                        "@NiceName": "Active",
                        "@Type": "xsd:boolean",
                        "@Name": "state",
                        "@isPropertyState": "true",
                    },
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
                    "source": {
                        "@NiceName": "Disk",
                        "@Type": "xsd:string",
                        "@Name": "disk_id",
                        "Value": ["SD_DISK", "NetworkShare"],
                    },
                    "data": [
                        {
                            "@NiceName": "Temperature",
                            "@Type": "xsd:int",
                            "@Name": "temperature",
                        },
                        {
                            "@isPropertyState": "true",
                            "@NiceName": "Alert",
                            "@Type": "xsd:boolean",
                            "@Name": "alert",
                        },
                        {"@NiceName": "Wear", "@Type": "xsd:int", "@Name": "wear"},
                        {
                            "@NiceName": "Overall Health",
                            "@Type": "xsd:int",
                            "@Name": "overall_health",
                        },
                    ],
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
                    "source": {},
                    "data": {
                        "@Type": "xsd:boolean",
                        "@Name": "active",
                        "@isPropertyState": "true",
                    },
                },
            },
        ),
    ],
)
async def test_single_event_instance(
    respx_mock, event_instances: EventInstanceHandler, response: str, expected: dict
):
    """Verify expected outcome from different event instances."""
    respx_mock.post("/vapix/services").respond(
        text=response, headers={"Content-Type": "application/soap+xml; charset=utf-8"}
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
