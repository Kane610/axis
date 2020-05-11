"""Test Axis event services.

pytest --cov-report term-missing --cov=axis.event_services tests/test_event_services.py
"""

from unittest.mock import MagicMock, Mock, patch
import pytest

from axis.event_services import get_event_list

from .event_fixtures import EVENT_INSTANCES


def test_get_event_list():
    """Verify device events list method."""
    mock_config = Mock()
    with patch(
        "axis.event_services.session_request", new=Mock(return_value=EVENT_INSTANCES)
    ):
        event_list = get_event_list(mock_config)

    assert "motion" not in event_list
    assert "vmd3" in event_list
    assert "pir" in event_list
    assert "sound" in event_list
    assert "daynight" in event_list
    assert "tampering" in event_list
    assert "input" not in event_list
    assert "vmd4" in event_list
