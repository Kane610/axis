"""Test Axis view area API.

pytest --cov-report term-missing --cov=axis.event_instances tests/test_event_instances.py
"""

import pytest

from axis.event_instances import EventInstances, URL
import respx

from .conftest import HOST
from .event_fixtures import EVENT_INSTANCES, EVENT_INSTANCE_VMD4_PROFILE1


@pytest.fixture
def event_instances(axis_device) -> EventInstances:
    """Returns the view_areas mock object."""
    return EventInstances(axis_device.vapix.request)


@respx.mock
async def test_full_list_of_event_instances(event_instances):
    """Test simple view area."""
    route = respx.post(f"http://{HOST}:80{URL}").respond(
        text=EVENT_INSTANCES,
        headers={"Content-Type": "application/soap+xml; charset=utf-8"},
    )

    await event_instances.update()

    assert len(event_instances) == 44
    # assert 0


@pytest.mark.parametrize(
    "response,id,expected",
    [
        (
            EVENT_INSTANCE_VMD4_PROFILE1,
            "tnsaxis:CameraApplicationPlatform/VMD/Camera1Profile1_",
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
        )
    ],
)
@respx.mock
async def test_single_event_instance(
    event_instances: EventInstances, response: bytes, id: str, expected: dict
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
    event.is_available == expected["is_available"]
    event.is_application_data == expected["is_application_data"]
    event.name == expected["name"]
    event.stateful == expected["message"]["stateful"]
    event.stateless == expected["message"]["stateless"]
    event.source == expected["message"]["source"]
    event.data == expected["message"]["data"]
