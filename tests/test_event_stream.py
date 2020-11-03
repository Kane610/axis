"""Test Axis event stream.

pytest --cov-report term-missing --cov=axis.event_stream tests/test_event_stream.py
"""

import pytest
from unittest.mock import Mock

from axis.event_stream import EventManager

from .event_fixtures import (
    FIRST_MESSAGE,
    AUDIO_INIT,
    DAYNIGHT_INIT,
    FENCE_GUARD_INIT,
    GLOBAL_SCENE_CHANGE,
    LIGHT_STATUS_INIT,
    LOITERING_GUARD_INIT,
    MOTION_GUARD_INIT,
    OBJECT_ANALYTICS_INIT,
    PIR_INIT,
    PIR_CHANGE,
    PORT_0_INIT,
    PORT_ANY_INIT,
    PTZ_MOVE_INIT,
    PTZ_MOVE_START,
    PTZ_MOVE_END,
    PTZ_PRESET_INIT_1,
    PTZ_PRESET_INIT_2,
    PTZ_PRESET_INIT_3,
    PTZ_PRESET_AT_1_TRUE,
    PTZ_PRESET_AT_1_FALSE,
    PTZ_PRESET_AT_2_TRUE,
    PTZ_PRESET_AT_2_FALSE,
    PTZ_PRESET_AT_3_TRUE,
    PTZ_PRESET_AT_3_FALSE,
    RELAY_INIT,
    VMD3_INIT,
    VMD4_ANY_INIT,
    VMD4_ANY_CHANGE,
)


@pytest.fixture
def event_manager() -> EventManager:
    """Returns mocked event manager."""
    signal = Mock()
    return EventManager(signal)


def test_parse_event_first_message(event_manager):
    """Verify that first message doesn't do anything."""
    assert not event_manager.parse_event_xml(FIRST_MESSAGE)


def test_parse_event_pir_init(event_manager):
    """Verify that PIR init can be parsed correctly."""
    pir = event_manager.parse_event_xml(PIR_INIT)
    assert pir == {
        "operation": "Initialized",
        "topic": "tns1:Device/tnsaxis:Sensor/PIR",
        "source": "sensor",
        "source_idx": "0",
        "type": "state",
        "value": "0",
    }


def test_parse_event_pir_change(event_manager):
    """Verify that PIR change can be parsed correctly"""
    pir = event_manager.parse_event_xml(PIR_CHANGE)
    assert pir == {
        "operation": "Changed",
        "topic": "tns1:Device/tnsaxis:Sensor/PIR",
        "source": "sensor",
        "source_idx": "0",
        "type": "state",
        "value": "1",
    }


def test_parse_event_pir_init(event_manager):
    """Verify that PIR init can be parsed correctly."""
    pir = event_manager.parse_event_xml(PIR_INIT)
    assert pir == {
        "operation": "Initialized",
        "topic": "tns1:Device/tnsaxis:Sensor/PIR",
        "source": "sensor",
        "source_idx": "0",
        "type": "state",
        "value": "0",
    }


def test_parse_event_pir_change(event_manager):
    """Verify that PIR change can be parsed correctly"""
    pir = event_manager.parse_event_xml(PIR_CHANGE)
    assert pir == {
        "operation": "Changed",
        "topic": "tns1:Device/tnsaxis:Sensor/PIR",
        "source": "sensor",
        "source_idx": "0",
        "type": "state",
        "value": "1",
    }


def test_parse_event_vmd4_init(event_manager):
    """Verify that VMD4 init can be parsed correctly."""
    vmd = event_manager.parse_event_xml(VMD4_ANY_INIT)
    assert vmd == {
        "operation": "Initialized",
        "topic": "tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY",
        "type": "active",
        "value": "0",
    }


def test_parse_event_vmd4_change(event_manager):
    """Verify that VMD4 change can be parsed correctly."""
    vmd = event_manager.parse_event_xml(VMD4_ANY_CHANGE)
    assert vmd == {
        "operation": "Changed",
        "topic": "tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY",
        "type": "active",
        "value": "1",
    }


def test_audio_init(event_manager):
    """Verify that a new audio event can be managed."""
    event_manager.update(AUDIO_INIT)

    event = next(iter(event_manager.values()))
    assert event.topic == "tns1:AudioSource/tnsaxis:TriggerLevel"
    assert event.source == "channel"
    assert event.id == "1"
    assert event.CLASS == "sound"
    assert event.TYPE == "Sound"
    assert event.state == "0"


def test_daynight_init(event_manager):
    """Verify that a new day/night event can be managed."""
    event_manager.update(DAYNIGHT_INIT)

    event = next(iter(event_manager.values()))
    assert event.topic == "tns1:VideoSource/tnsaxis:DayNightVision"
    assert event.source == "VideoSourceConfigurationToken"
    assert event.id == "1"
    assert event.CLASS == "light"
    assert event.TYPE == "DayNight"
    assert event.state == "1"


def test_fence_guard_init(event_manager):
    """Verify that a new fence guard event can be managed."""
    event_manager.update(FENCE_GUARD_INIT)

    event = next(iter(event_manager.values()))
    assert event.topic == "tnsaxis:CameraApplicationPlatform/FenceGuard/Camera1Profile1"
    assert event.source == ""
    assert event.id == "Camera1Profile1"
    assert event.CLASS == "motion"
    assert event.TYPE == "Fence Guard"
    assert event.state == "0"


def test_light_status_init(event_manager):
    """Verify that a new day/night event can be managed."""
    event_manager.update(LIGHT_STATUS_INIT)

    event = next(iter(event_manager.values()))
    assert event.topic == "tns1:Device/tnsaxis:Light/Status"
    assert event.source == "id"
    assert event.id == "0"
    assert event.CLASS == "light"
    assert event.TYPE == "Light"
    assert event.state == "OFF"
    assert event.is_tripped is False


def test_loitering_guard_init(event_manager):
    """Verify that a new loitering guard event can be managed."""
    event_manager.update(LOITERING_GUARD_INIT)

    event = next(iter(event_manager.values()))
    assert (
        event.topic
        == "tnsaxis:CameraApplicationPlatform/LoiteringGuard/Camera1Profile1"
    )
    assert event.source == ""
    assert event.id == "Camera1Profile1"
    assert event.CLASS == "motion"
    assert event.TYPE == "Loitering Guard"
    assert event.state == "0"


def test_motion_guard_init(event_manager):
    """Verify that a new loitering guard event can be managed."""
    event_manager.update(MOTION_GUARD_INIT)

    event = next(iter(event_manager.values()))
    assert (
        event.topic == "tnsaxis:CameraApplicationPlatform/MotionGuard/Camera1ProfileANY"
    )
    assert event.source == ""
    assert event.id == "Camera1ProfileANY"
    assert event.CLASS == "motion"
    assert event.TYPE == "Motion Guard"
    assert event.state == "0"


def test_object_analytics_init(event_manager):
    """Verify that a new object analytics event can be managed."""
    event_manager.update(OBJECT_ANALYTICS_INIT)

    event = next(iter(event_manager.values()))
    assert (
        event.topic
        == "tnsaxis:CameraApplicationPlatform/ObjectAnalytics/Device1Scenario1"
    )
    assert event.source == ""
    assert event.id == "Device1Scenario1"
    assert event.CLASS == "motion"
    assert event.TYPE == "Object Analytics"
    assert event.state == "0"


def test_port_0_init(event_manager):
    """Verify that a new day/night event can be managed."""
    event_manager.update(PORT_0_INIT)

    event = next(iter(event_manager.values()))
    assert event.topic == "tns1:Device/tnsaxis:IO/Port"
    assert event.source == "port"
    assert event.id == "1"
    assert event.CLASS == "input"
    assert event.TYPE == "Input"
    assert event.state == "0"


def test_port_any_init(event_manager):
    """Verify that a new day/night event can be managed."""
    event_manager.update(PORT_ANY_INIT)

    event = next(iter(event_manager.values()))
    assert event.topic == "tns1:Device/tnsaxis:IO/Port"
    assert event.CLASS == "input"
    assert event.TYPE == "Input"
    assert event.state == "0"


def test_pir_init(event_manager):
    """Verify that a new PIR event can be managed."""
    event_manager.update(PIR_INIT)
    assert event_manager.values()

    event = next(iter(event_manager.values()))
    assert event.topic == "tns1:Device/tnsaxis:Sensor/PIR"
    assert event.source == "sensor"
    assert event.id == "0"
    assert event.CLASS == "motion"
    assert event.TYPE == "PIR"
    assert event.state == "0"

    mock_callback = Mock()
    event.register_callback(mock_callback)

    event_manager.update(PIR_CHANGE)
    assert event.state == "1"
    assert event.is_tripped
    assert mock_callback.called

    event.remove_callback(mock_callback)
    assert not event.observers


def test_pir_change(event_manager):
    """Verify that a PIR event change can be managed."""
    event_manager.update(PIR_INIT)
    event_manager.update(PIR_CHANGE)

    event = next(iter(event_manager.values()))
    assert event.state == "1"


def test_ptz_preset(event_manager):
    """Verify that a new PTZ preset event can be managed."""
    event_manager.update(PTZ_PRESET_INIT_1)
    event_manager.update(PTZ_PRESET_INIT_2)
    event_manager.update(PTZ_PRESET_INIT_3)

    events = iter(event_manager.values())

    event_1 = next(events)
    assert event_1.topic == "tns1:PTZController/tnsaxis:PTZPresets/Channel_1"
    assert event_1.source == "PresetToken"
    assert event_1.id == "1"
    assert event_1.CLASS == "ptz"
    assert event_1.TYPE == "on_preset"
    assert event_1.state == "1"

    event_2 = next(events)
    assert event_2.id == "2"
    assert event_2.state == "0"

    event_3 = next(events)
    assert event_3.id == "3"
    assert event_3.state == "0"

    for event in (event_1, event_2, event_3):
        mock_callback = Mock()
        event.register_callback(mock_callback)

    event_manager.update(PTZ_PRESET_AT_1_FALSE)
    assert event_1.state == "0"
    assert not event_1.is_tripped
    assert event_2.state == "0"
    assert not event_2.is_tripped
    assert event_3.state == "0"
    assert not event_3.is_tripped

    event_manager.update(PTZ_PRESET_AT_2_TRUE)
    assert event_1.state == "0"
    assert not event_1.is_tripped
    assert event_2.state == "1"
    assert event_2.is_tripped
    assert event_3.state == "0"
    assert not event_3.is_tripped

    event_manager.update(PTZ_PRESET_AT_2_FALSE)
    assert event_1.state == "0"
    assert not event_1.is_tripped
    assert event_2.state == "0"
    assert not event_2.is_tripped
    assert event_3.state == "0"
    assert not event_3.is_tripped

    event_manager.update(PTZ_PRESET_AT_3_TRUE)
    assert event_1.state == "0"
    assert not event_1.is_tripped
    assert event_2.state == "0"
    assert not event_2.is_tripped
    assert event_3.state == "1"
    assert event_3.is_tripped

    event_manager.update(PTZ_PRESET_AT_3_FALSE)
    assert event_1.state == "0"
    assert not event_1.is_tripped
    assert event_2.state == "0"
    assert not event_2.is_tripped
    assert event_3.state == "0"
    assert not event_3.is_tripped

    event_manager.update(PTZ_PRESET_AT_1_TRUE)
    assert event_1.state == "1"
    assert event_1.is_tripped
    assert event_2.state == "0"
    assert not event_2.is_tripped
    assert event_3.state == "0"
    assert not event_3.is_tripped


def test_ptz_move(event_manager):
    """Verify that a new PTZ move event can be managed."""
    event_manager.update(PTZ_MOVE_INIT)

    event = next(iter(event_manager.values()))
    assert event.topic == "tns1:PTZController/tnsaxis:Move/Channel_1"
    assert event.source == "PTZConfigurationToken"
    assert event.id == "1"
    assert event.CLASS == "ptz"
    assert event.TYPE == "is_moving"
    assert event.state == "0"

    mock_callback = Mock()
    event.register_callback(mock_callback)

    event_manager.update(PTZ_MOVE_START)
    assert event.state == "1"
    assert event.is_tripped
    assert mock_callback.called

    event_manager.update(PTZ_MOVE_END)
    assert event.state == "0"
    assert not event.is_tripped
    assert mock_callback.called

    event.remove_callback(mock_callback)
    assert not event.observers


def test_relay_init(event_manager):
    """Verify that a new day/night event can be managed."""
    event_manager.update(RELAY_INIT)

    event = next(iter(event_manager.values()))
    assert event.topic == "tns1:Device/Trigger/Relay"
    assert event.source == "RelayToken"
    assert event.id == "3"
    assert event.CLASS == "output"
    assert event.TYPE == "Relay"
    assert event.state == "inactive"


def test_vmd3_init(event_manager):
    """Verify that a new VMD3 event can be managed."""
    event_manager.update(VMD3_INIT)

    event = next(iter(event_manager.values()))
    assert event.topic == "tns1:RuleEngine/tnsaxis:VMD3/vmd3_video_1"
    assert event.source == "areaid"
    assert event.id == "0"
    assert event.CLASS == "motion"
    assert event.TYPE == "VMD3"
    assert event.state == "0"


def test_vmd4_init(event_manager):
    """Verify that a new VMD4 event can be managed."""
    event_manager.update(VMD4_ANY_INIT)

    event = next(iter(event_manager.values()))
    assert event.topic == "tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY"
    assert not event.source
    assert event.id == "Camera1ProfileANY"
    assert event.CLASS == "motion"
    assert event.TYPE == "VMD4"
    assert event.state == "0"


def test_vmd4_change(event_manager):
    """Verify that a VMD4 event change can be managed."""
    event_manager.update(VMD4_ANY_INIT)
    event_manager.update(VMD4_ANY_CHANGE)

    event = next(iter(event_manager.values()))
    assert event.state == "1"


def test_unsupported_event(event_manager):
    """Verify that unsupported events aren't created."""
    event_manager.update(GLOBAL_SCENE_CHANGE)

    event = next(iter(event_manager.values()))
    assert event.BINARY is False
    assert event.TOPIC is None
    assert event.CLASS is None
    assert event.TYPE is None
    assert event.topic == "tns1:VideoSource/GlobalSceneChange/ImagingService"
    assert event.source == "Source"
    assert event.id == "0"
    assert event.state == "0"


def test_initialize_event_already_exist(event_manager):
    """Verify that initialize with an already existing event doesn't create."""
    event_manager.update(VMD4_ANY_INIT)
    assert event_manager.values()

    event_manager.update(VMD4_ANY_INIT)
    assert len(event_manager.values()) == 1
