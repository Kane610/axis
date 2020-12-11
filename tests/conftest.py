"""Setup common test helpers."""

import pytest

from axis.configuration import Configuration
from axis.device import AxisDevice
from httpx import AsyncClient


@pytest.fixture
async def axis_device(loop) -> AxisDevice:
    """Returns the axis device.

    Clean up sessions automatically at the end of each test.
    """
    session = AsyncClient(verify=False)
    axis_device = AxisDevice(
        Configuration(session, "host", username="root", password="pass")
    )
    yield axis_device
    await session.aclose()