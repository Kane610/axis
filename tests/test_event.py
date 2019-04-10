"""Test Axis events.

pytest --cov-report term-missing --cov=axis.event tests/test_event.py
"""

from unittest.mock import MagicMock, Mock, patch
import pytest

from axis.event import EventManager, get_event_list

from .event_fixtures import (
    FIRST_MESSAGE, PIR_INIT, PIR_CHANGE, VMD4_ANY_INIT, VMD4_ANY_CHANGE,
    VMD4_C1P1_INIT, VMD4_C1P1_CHANGE, VMD4_C1P2_INIT, VMD4_C1P2_CHANGE,
    EVENT_INSTANCES)


@pytest.fixture
def manager() -> EventManager:
    """Returns mocked event manager."""
    event_types = False
    signal = Mock()
    return EventManager(event_types, signal)


def test_eventmanager(manager):
    """Verify query is set to off if event types is empty."""
    assert manager.query == 'off'


def test_create_event_set_to_on(manager):
    """Verify that an event query can be created."""
    assert manager.create_event_query(True) == 'on'


def test_create_event_query_single_topic(manager):
    """Verify that an event query can be created."""
    assert manager.create_event_query(
        'pir') == 'on&eventtopic=onvif:Device/axis:Sensor/PIR'


def test_create_event_query_multiple_topics(manager):
    """Verify that an event query can be created with multiple topics."""
    assert manager.create_event_query(
        ['pir', 'input']) == 'on&eventtopic=onvif:Device/axis:Sensor/PIR|onvif:Device/axis:IO/Port'


def test_parse_event_first_message(manager):
    """Verify that first message doesn't do anything."""
    assert not manager.parse_event_xml(FIRST_MESSAGE)


def test_parse_event_pir_init(manager):
    """Verify that PIR init can be parsed correctly."""
    pir = manager.parse_event_xml(PIR_INIT)
    assert pir == {
        'operation': 'Initialized',
        'topic': 'tns1:Device/tnsaxis:Sensor/PIR',
        'source': 'sensor',
        'source_idx': '0',
        'type': 'state',
        'value': '0'
    }


def test_parse_event_pir_change(manager):
    """Verify that PIR change can be parsed correctly"""
    pir = manager.parse_event_xml(PIR_CHANGE)
    assert pir == {
        'operation': 'Changed',
        'topic': 'tns1:Device/tnsaxis:Sensor/PIR',
        'source': 'sensor',
        'source_idx': '0',
        'type': 'state',
        'value': '1'
    }


def test_parse_event_vmd4_init(manager):
    """Verify that VMD4 init can be parsed correctly."""
    vmd = manager.parse_event_xml(VMD4_ANY_INIT)
    assert vmd == {
        'operation': 'Initialized',
        'topic': 'tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY',
        'type': 'active',
        'value': '0'
    }


def test_parse_event_vmd4_change(manager):
    """Verify that VMD4 change can be parsed correctly."""
    vmd = manager.parse_event_xml(VMD4_ANY_CHANGE)
    assert vmd == {
        'operation': 'Changed',
        'topic': 'tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY',
        'type': 'active',
        'value': '1'
    }


def test_manage_event_pir_init(manager):
    """Verify that a new PIR event can be managed."""
    manager.new_event(PIR_INIT)
    assert manager.events

    event = manager.events['tns1:Device/tnsaxis:Sensor/PIR_0']
    assert event.topic == 'tns1:Device/tnsaxis:Sensor/PIR'
    assert event.source == 'sensor'
    assert event.id == '0'
    assert event.event_class == 'motion'
    assert event.event_type == 'PIR'
    assert event.state == '0'

    mock_callback = Mock()
    event.register_callback(mock_callback)
    event.state = '1'
    assert event.state == '1'
    assert event.is_tripped
    assert mock_callback.called
    assert 'callback' not in event.as_dict()

    event.remove_callback(mock_callback)
    assert not event._callbacks


def test_manage_event_pir_change(manager):
    """Verify that a PIR event change can be managed."""
    manager.new_event(PIR_INIT)
    manager.new_event(PIR_CHANGE)

    event = manager.events['tns1:Device/tnsaxis:Sensor/PIR_0']
    assert event.state == '1'


def test_manage_event_vmd4_init(manager):
    """Verify that a new VMD4 event can be managed."""
    manager.new_event(VMD4_ANY_INIT)
    assert manager.events

    event = manager.events['tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY_None']
    assert event.topic == 'tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY'
    assert not event.source
    assert event.id == 'Camera1ProfileANY'
    assert event.event_class == 'motion'
    assert event.event_type == 'VMD4'
    assert event.state == '0'


def test_manage_event_vmd4_change(manager):
    """Verify that a VMD4 event change can be managed."""
    manager.new_event(VMD4_ANY_INIT)
    manager.new_event(VMD4_ANY_CHANGE)

    event = manager.events['tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY_None']
    assert event.state == '1'


def test_get_event_list():
    """Verify device events list method."""
    mock_config = Mock()
    with patch('axis.event.session_request',
               new=Mock(return_value=EVENT_INSTANCES)):
        event_list = get_event_list(mock_config)

    assert 'motion' not in event_list
    assert 'vmd3' in event_list
    assert 'pir' in event_list
    assert 'sound' in event_list
    assert 'daynight' in event_list
    assert 'tampering' in event_list
    assert 'input' not in event_list
    assert 'vmd4' in event_list
