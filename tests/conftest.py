"""Setup common test helpers."""

import pytest

from axis.configuration import Configuration
from axis.device import AxisDevice


@pytest.fixture
async def axis_device(loop) -> AxisDevice:
    """Returns the axis device.

    Clean up sessions automatically at the end of each test.
    """
    axis_device = AxisDevice(Configuration("host", username="root", password="pass"))
    yield axis_device
    await axis_device.vapix.close()