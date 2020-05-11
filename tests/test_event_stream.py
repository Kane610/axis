"""Test Axis event stream.

pytest --cov-report term-missing --cov=axis.event_stream tests/test_event_stream.py
"""

from unittest.mock import Mock, patch
import pytest

from axis.event_stream import EventManager

from .event_fixtures import (
    FIRST_MESSAGE,
    AUDIO_INIT,
    DAYNIGHT_INIT,
    PIR_INIT,
    PIR_CHANGE,
    PORT_0_INIT,
    PORT_ANY_INIT,
    RELAY_INIT,
    VMD3_INIT,
    VMD4_ANY_INIT,
    VMD4_ANY_CHANGE,
    VMD4_C1P1_INIT,
    VMD4_C1P1_CHANGE,
    VMD4_C1P2_INIT,
    VMD4_C1P2_CHANGE,
)


@pytest.fixture
def manager() -> EventManager:
    """Returns mocked event manager."""
    signal = Mock()
    return EventManager(signal)


def test_parse_event_first_message(manager):
    """Verify that first message doesn't do anything."""
    assert not manager.parse_event_xml(FIRST_MESSAGE)


def test_parse_event_pir_init(manager):
    """Verify that PIR init can be parsed correctly."""
    pir = manager.parse_event_xml(PIR_INIT)
    assert pir == {
        "operation": "Initialized",
        "topic": "tns1:Device/tnsaxis:Sensor/PIR",
        "source": "sensor",
        "source_idx": "0",
        "type": "state",
        "value": "0",
    }


def test_parse_event_pir_change(manager):
    """Verify that PIR change can be parsed correctly"""
    pir = manager.parse_event_xml(PIR_CHANGE)
    assert pir == {
        "operation": "Changed",
        "topic": "tns1:Device/tnsaxis:Sensor/PIR",
        "source": "sensor",
        "source_idx": "0",
        "type": "state",
        "value": "1",
    }


def test_parse_event_vmd4_init(manager):
    """Verify that VMD4 init can be parsed correctly."""
    vmd = manager.parse_event_xml(VMD4_ANY_INIT)
    assert vmd == {
        "operation": "Initialized",
        "topic": "tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY",
        "type": "active",
        "value": "0",
    }


def test_parse_event_vmd4_change(manager):
    """Verify that VMD4 change can be parsed correctly."""
    vmd = manager.parse_event_xml(VMD4_ANY_CHANGE)
    assert vmd == {
        "operation": "Changed",
        "topic": "tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY",
        "type": "active",
        "value": "1",
    }


def test_manage_event_audio_init(manager):
    """Verify that a new audio event can be managed."""
    manager.new_event(AUDIO_INIT)

    event = manager.events["tns1:AudioSource/tnsaxis:TriggerLevel_1"]
    assert event.topic == "tns1:AudioSource/tnsaxis:TriggerLevel"
    assert event.source == "channel"
    assert event.id == "1"
    assert event.CLASS == "sound"
    assert event.TYPE == "Sound"
    assert event.state == "0"


def test_manage_event_daynight_init(manager):
    """Verify that a new day/night event can be managed."""
    manager.new_event(DAYNIGHT_INIT)

    event = manager.events["tns1:VideoSource/tnsaxis:DayNightVision_1"]
    assert event.topic == "tns1:VideoSource/tnsaxis:DayNightVision"
    assert event.source == "VideoSourceConfigurationToken"
    assert event.id == "1"
    assert event.CLASS == "light"
    assert event.TYPE == "DayNight"
    assert event.state == "1"


def test_manage_event_port_0_init(manager):
    """Verify that a new day/night event can be managed."""
    manager.new_event(PORT_0_INIT)

    event = manager.events["tns1:Device/tnsaxis:IO/Port_1"]
    assert event.topic == "tns1:Device/tnsaxis:IO/Port"
    assert event.source == "port"
    assert event.id == "1"
    assert event.CLASS == "input"
    assert event.TYPE == "Input"
    assert event.state == "0"


def test_manage_event_port_any_init(manager):
    """Verify that a new day/night event can be managed."""
    manager.new_event(PORT_ANY_INIT)

    event = manager.events["tns1:Device/tnsaxis:IO/Port_None"]
    assert event.topic == "tns1:Device/tnsaxis:IO/Port"
    assert event.CLASS == "input"
    assert event.TYPE == "Input"
    assert event.state == "0"


def test_manage_event_pir_init(manager):
    """Verify that a new PIR event can be managed."""
    manager.new_event(PIR_INIT)
    assert manager.events

    event = manager.events["tns1:Device/tnsaxis:Sensor/PIR_0"]
    assert event.topic == "tns1:Device/tnsaxis:Sensor/PIR"
    assert event.source == "sensor"
    assert event.id == "0"
    assert event.CLASS == "motion"
    assert event.TYPE == "PIR"
    assert event.state == "0"

    mock_callback = Mock()
    event.register_callback(mock_callback)
    event.state = "1"
    assert event.state == "1"
    assert event.is_tripped
    assert mock_callback.called

    event.remove_callback(mock_callback)
    assert not event._callbacks


def test_manage_event_pir_change(manager):
    """Verify that a PIR event change can be managed."""
    manager.new_event(PIR_INIT)
    manager.new_event(PIR_CHANGE)

    event = manager.events["tns1:Device/tnsaxis:Sensor/PIR_0"]
    assert event.state == "1"


def test_manage_event_port_any_init(manager):
    """Verify that a new day/night event can be managed."""
    manager.new_event(RELAY_INIT)

    event = manager.events["tns1:Device/Trigger/Relay_3"]
    assert event.topic == "tns1:Device/Trigger/Relay"
    assert event.source == "RelayToken"
    assert event.id == "3"
    assert event.CLASS == "output"
    assert event.TYPE == "Relay"
    assert event.state == "inactive"


def test_manage_event_vmd3_init(manager):
    """Verify that a new VMD3 event can be managed."""
    manager.new_event(VMD3_INIT)

    event = manager.events["tns1:RuleEngine/tnsaxis:VMD3/vmd3_video_1_0"]
    assert event.topic == "tns1:RuleEngine/tnsaxis:VMD3/vmd3_video_1"
    assert event.source == "areaid"
    assert event.id == "0"
    assert event.CLASS == "motion"
    assert event.TYPE == "VMD3"
    assert event.state == "0"


def test_manage_event_vmd4_init(manager):
    """Verify that a new VMD4 event can be managed."""
    manager.new_event(VMD4_ANY_INIT)

    event = manager.events[
        "tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY_None"
    ]
    assert event.topic == "tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY"
    assert not event.source
    assert event.id == "Camera1ProfileANY"
    assert event.CLASS == "motion"
    assert event.TYPE == "VMD4"
    assert event.state == "0"


def test_manage_event_vmd4_change(manager):
    """Verify that a VMD4 event change can be managed."""
    manager.new_event(VMD4_ANY_INIT)
    manager.new_event(VMD4_ANY_CHANGE)

    event = manager.events[
        "tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY_None"
    ]
    assert event.state == "1"


def test_manage_event_unsupported_event(manager):
    """Verify that unsupported events aren't created."""
    event = {"operation": "Initialized", "topic": "unsupported_topic"}
    manager.manage_event(event)
    assert not manager.events


def test_manage_event_initialize_event_already_exist(manager):
    """Verify that initialize with an already existing event doesn't create."""
    manager.new_event(VMD4_ANY_INIT)
    assert manager.events

    manager.new_event(VMD4_ANY_INIT)
    assert len(manager.events) == 1
