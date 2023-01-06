"""Test AxisDevice main class.

pytest --cov-report term-missing --cov=axis.device tests/test_device.py
"""

from unittest.mock import Mock


def test_device(axis_device):
    """Validate Axis device class."""
    assert axis_device.config
    assert axis_device.vapix
    assert axis_device.stream
    assert axis_device.event is not None
    assert len(axis_device.event) == 0

    axis_device.enable_events()
    axis_device.event.subscribe(Mock())
    assert len(axis_device.event) == 1
