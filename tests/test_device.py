"""Test AxisDevice main class.

pytest --cov-report term-missing --cov=axis.device tests/test_device.py
"""

from unittest.mock import Mock

from axis.configuration import Configuration
from axis.device import AxisDevice


def test_device():
    """"""
    axis_device = AxisDevice(
        Configuration("host", port=80, username="root", password="pass")
    )

    assert axis_device.config
    assert axis_device.vapix
    assert axis_device.stream
    assert axis_device.event is None

    mock_callback = Mock()
    axis_device.enable_events(mock_callback)
    assert axis_device.event
    assert axis_device.event.signal == mock_callback
