"""Test Axis events.

pytest --cov-report term-missing --cov=axis.event tests/test_event.py
"""

from unittest.mock import Mock, patch
import pytest

from axis.event import EventManager
from .event_fixtures import (
    FIRST_MESSAGE, PIR_INIT, PIR_CHANGE, VMD4_ANY_INIT, VMD4_ANY_CHANGE,
    VMD4_C1P1_INIT, VMD4_C1P1_CHANGE, VMD4_C1P2_INIT, VMD4_C1P2_CHANGE,
    EVENT_INSTANCES)


@pytest.fixture
def manager() -> EventManager:
    """Returns mocked event manager."""
    event_types = ''
    signal = Mock()
    return EventManager(event_types, signal)


def test_eventmanager(manager):
    """Verify query is set to off if event types is empty."""
    assert manager.query == 'off'


def test_parse_event_first_message(manager):
    """Verify that first message doesn't do anything."""
    assert not manager._parse_event(FIRST_MESSAGE)


def test_parse_event_pir_init(manager):
    """Verify that PIR init can be parsed correctly."""
    pir = manager._parse_event(PIR_INIT)
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
    pir = manager._parse_event(PIR_CHANGE)
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
    vmd = manager._parse_event(VMD4_ANY_INIT)
    assert vmd == {
        'operation': 'Initialized',
        'topic': 'tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY',
        'type': 'active',
        'value': '0'
    }


def test_parse_event_vmd4_change(manager):
    """Verify that VMD4 change can be parsed correctly."""
    vmd = manager._parse_event(VMD4_ANY_CHANGE)
    assert vmd == {
        'operation': 'Changed',
        'topic': 'tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY',
        'type': 'active',
        'value': '1'
    }


def test_manage_event_pir_init(manager):
    """Verify that a new PIR event can be managed."""
    manager.manage_event(PIR_INIT)
    assert manager.events

    event = manager.events['tns1:Device/tnsaxis:Sensor/PIR_0']
    assert event.topic == 'tns1:Device/tnsaxis:Sensor/PIR'
    assert event.source == 'sensor'
    assert event.id == '0'
    assert event.event_class == 'motion'
    assert event.event_type == 'pir'
    assert event.event_platform == 'binary_sensor'
    assert not event.state


def test_manage_event_pir_change(manager):
    """Verify that a PIR event change can be managed."""
    manager.manage_event(PIR_INIT)
    manager.manage_event(PIR_CHANGE)

    event = manager.events['tns1:Device/tnsaxis:Sensor/PIR_0']
    assert event.state == '1'


def test_manage_event_vmd4_init(manager):
    """Verify that a new VMD4 event can be managed."""
    manager.manage_event(VMD4_ANY_INIT)
    assert manager.events

    event = manager.events['tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY_None']
    assert event.topic == 'tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY'
    assert not event.source
    assert event.id == None
    assert event.event_class == 'motion'
    assert event.event_type == 'vmd4'
    assert event.event_platform == 'binary_sensor'
    assert not event.state


def test_manage_event_vmd4_change(manager):
    """Verify that a VMD4 event change can be managed."""
    manager.manage_event(VMD4_ANY_INIT)
    manager.manage_event(VMD4_ANY_CHANGE)

    event = manager.events['tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY_None']
    assert event.state == '1'

from axis.event import _prepare_event


def test_prepare_event():
    from pprint import pprint
    pprint(_prepare_event(EVENT_INSTANCES))
    assert False
