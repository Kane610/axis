"""Test Axis view area API.

pytest --cov-report term-missing --cov=axis.event_instances tests/test_event_instances.py
"""

import pytest

from axis.event_instances import EventInstances, URL
import respx

from .conftest import HOST
from .event_fixtures import EVENT_INSTANCES


@pytest.fixture
def event_instances(axis_device) -> EventInstances:
    """Returns the view_areas mock object."""
    return EventInstances(axis_device.vapix.request)


@respx.mock
async def test_list_view_areas(event_instances):
    """Test simple view area."""
    route = respx.post(f"http://{HOST}:80{URL}").respond(
        text=EVENT_INSTANCES, headers={"Content-Type": "text/plain"}
    )

    await event_instances.update()
    assert 0
