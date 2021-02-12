"""Test Axis event instance API.

pytest --cov-report term-missing --cov=axis.event_instances tests/test_event_instances.py
"""

import pytest

from axis.event_instances import EventInstances, URL, get_events
import respx

from .conftest import HOST
from .event_fixtures import (
    EVENT_INSTANCES,
    EVENT_INSTANCE_PIR_SENSOR,
    EVENT_INSTANCE_VMD4_PROFILE1,
)


@pytest.fixture
def event_instances(axis_device) -> EventInstances:
    """Returns the view_areas mock object."""
    return EventInstances(axis_device.vapix.request)


@respx.mock
async def test_full_list_of_event_instances(event_instances):
    """Test simple view area."""
    respx.post(f"http://{HOST}:80{URL}").respond(
        text=EVENT_INSTANCES,
        headers={"Content-Type": "application/soap+xml; charset=utf-8"},
    )
    await event_instances.update()

    assert len(event_instances) == 44


@pytest.mark.parametrize(
    "response,id,topic_filter,expected",
    [
        (
            EVENT_INSTANCE_PIR_SENSOR,
            "tns1:Device/tnsaxis:Sensor/PIR_0",
            "onvif:Device/axis:Sensor/PIR",
            {
                "topic": "tns1:Device/tnsaxis:Sensor/PIR",
                "is_available": True,
                "is_application_data": False,
                "name": "PIR sensor",
                "message": {
                    "stateful": True,
                    "stateless": False,
                    "source": {
                        "@NiceName": "Sensor",
                        "@Type": "x:d:int",
                        "@Name": "sensor",
                        "Value": "0",
                    },
                    "data": {
                        "@NiceName": "Active",
                        "@Type": "x:d:boolean",
                        "@Name": "state",
                        "@isPropertyState": "true",
                    },
                },
            },
        ),
        (
            EVENT_INSTANCE_VMD4_PROFILE1,
            "tnsaxis:CameraApplicationPlatform/VMD/Camera1Profile1_",
            "axis:CameraApplicationPlatform/VMD/Camera1Profile1",
            {
                "topic": "tnsaxis:CameraApplicationPlatform/VMD/Camera1Profile1",
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
@respx.mock
async def test_single_event_instance(
    event_instances: EventInstances,
    response: bytes,
    id: str,
    topic_filter: str,
    expected: dict,
):
    """Test simple view area."""
    respx.post(f"http://{HOST}:80{URL}").respond(
        text=response, headers={"Content-Type": "application/soap+xml; charset=utf-8"}
    )
    await event_instances.update()

    assert len(event_instances) == 1

    assert id in event_instances
    event = event_instances[id]
    event.raw == expected
    event.topic == expected["topic"]
    event.topic_filter == topic_filter
    event.is_available == expected["is_available"]
    event.is_application_data == expected["is_application_data"]
    event.name == expected["name"]
    event.stateful == expected["message"]["stateful"]
    event.stateless == expected["message"]["stateless"]
    event.source == expected["message"]["source"]
    event.data == expected["message"]["data"]


@pytest.mark.parametrize(
    "input,output",
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
                }
            ],
        ),
    ],
)
async def test_get_events(input: dict, output: list):
    """Verify expected output of get_events."""
    assert get_events(input) == output
