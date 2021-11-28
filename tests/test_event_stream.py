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
    DOOR_MODE_INIT,
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
    RULE_ENGINE_REGION_DETECTOR_INIT,
    STORAGE_ALERT_INIT,
    VMD3_INIT,
    VMD4_ANY_INIT,
    VMD4_ANY_CHANGE,
)


@pytest.fixture
def event_manager(axis_device) -> EventManager:
    """Returns mocked event manager."""
    axis_device.enable_events(Mock())
    return axis_device.event


@pytest.mark.parametrize(
    "input,expected",
    [
        (FIRST_MESSAGE, {}),
        (
                PIR_INIT,
                {
                    "operation": "Initialized",
                    "topic": "tns1:Device/tnsaxis:Sensor/PIR",
                    "source": "sensor",
                    "source_idx": "0",
                    "type": "state",
                    "value": "0",
                },
        ),
        (
                PIR_CHANGE,
                {
                    "operation": "Changed",
                    "topic": "tns1:Device/tnsaxis:Sensor/PIR",
                    "source": "sensor",
                    "source_idx": "0",
                    "type": "state",
                    "value": "1",
                },
        ),
        (
                RULE_ENGINE_REGION_DETECTOR_INIT,
                {
                    "operation": "Initialized",
                    "source": "VideoSource",
                    "source_idx": "0",
                    "topic": "tns1:RuleEngine/MotionRegionDetector/Motion",
                    "type": "State",
                    "value": "0",
                },
        ),
        (
                STORAGE_ALERT_INIT,
                {
                    "operation": "Initialized",
                    "source": "disk_id",
                    "source_idx": "NetworkShare",
                    "topic": "tnsaxis:Storage/Alert",
                    "type": "overall_health",
                    "value": "-3",
                },
        ),
        (
                VMD4_ANY_INIT,
                {
                    "operation": "Initialized",
                    "topic": "tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY",
                    "type": "active",
                    "value": "0",
                },
        ),
        (
                VMD4_ANY_CHANGE,
                {
                    "operation": "Changed",
                    "topic": "tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY",
                    "type": "active",
                    "value": "1",
                },
        ),
    ],
)
def test_parse_event_xml(event_manager, input: bytes, expected: dict):
    """Verify that first message doesn't do anything."""
    assert event_manager.parse_event_xml(input) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        (
                AUDIO_INIT,
                {
                    "topic": "tns1:AudioSource/tnsaxis:TriggerLevel",
                    "source": "channel",
                    "source_idx": "1",
                    "class": "sound",
                    "type": "Sound",
                    "state": "0",
                    "tripped": False,
                },
        ),
        (
                DAYNIGHT_INIT,
                {
                    "topic": "tns1:VideoSource/tnsaxis:DayNightVision",
                    "source": "VideoSourceConfigurationToken",
                    "source_idx": "1",
                    "class": "light",
                    "type": "DayNight",
                    "state": "1",
                    "tripped": True,
                },
        ),
        (
                DOOR_MODE_INIT,
                {
                    "topic": "tns1:Door/State/DoorMode",
                    "source": "DoorToken",
                    "source_idx": "Axis-5fba94a4-8601-4627-bdda-cc408f69e026",
                    "class": "door",
                    "type": "Door Mode",
                    "state": "Accessed",
                    "tripped": False,
                },
        ),
        (
                FENCE_GUARD_INIT,
                {
                    "topic": "tnsaxis:CameraApplicationPlatform/FenceGuard/Camera1Profile1",
                    "source": "",
                    "source_idx": "Camera1Profile1",
                    "class": "motion",
                    "type": "Fence Guard",
                    "state": "0",
                    "tripped": False,
                },
        ),
        (
                LIGHT_STATUS_INIT,
                {
                    "topic": "tns1:Device/tnsaxis:Light/Status",
                    "source": "id",
                    "source_idx": "0",
                    "class": "light",
                    "type": "Light",
                    "state": "OFF",
                    "tripped": False,
                },
        ),
        (
                LOITERING_GUARD_INIT,
                {
                    "topic": "tnsaxis:CameraApplicationPlatform/LoiteringGuard/Camera1Profile1",
                    "source": "",
                    "source_idx": "Camera1Profile1",
                    "class": "motion",
                    "type": "Loitering Guard",
                    "state": "0",
                    "tripped": False,
                },
        ),
        (
                MOTION_GUARD_INIT,
                {
                    "topic": "tnsaxis:CameraApplicationPlatform/MotionGuard/Camera1ProfileANY",
                    "source": "",
                    "source_idx": "Camera1ProfileANY",
                    "class": "motion",
                    "type": "Motion Guard",
                    "state": "0",
                    "tripped": False,
                },
        ),
        (
                OBJECT_ANALYTICS_INIT,
                {
                    "topic": "tnsaxis:CameraApplicationPlatform/ObjectAnalytics/Device1Scenario1",
                    "source": "",
                    "source_idx": "Device1Scenario1",
                    "class": "motion",
                    "type": "Object Analytics",
                    "state": "0",
                    "tripped": False,
                },
        ),
        (
                PIR_INIT,
                {
                    "topic": "tns1:Device/tnsaxis:Sensor/PIR",
                    "source": "sensor",
                    "source_idx": "0",
                    "class": "motion",
                    "type": "PIR",
                    "state": "0",
                    "tripped": False,
                },
        ),
        (
                PORT_0_INIT,
                {
                    "topic": "tns1:Device/tnsaxis:IO/Port",
                    "source": "port",
                    "source_idx": "1",
                    "class": "input",
                    "type": "Input",
                    "state": "0",
                    "tripped": False,
                },
        ),
        (
                PORT_ANY_INIT,
                {
                    "topic": "tns1:Device/tnsaxis:IO/Port",
                    "source": "port",
                    "source_idx": "",
                    "class": "input",
                    "type": "Input",
                    "state": "0",
                    "tripped": False,
                },
        ),
        (
                PTZ_MOVE_INIT,
                {
                    "topic": "tns1:PTZController/tnsaxis:Move/Channel_1",
                    "source": "PTZConfigurationToken",
                    "source_idx": "1",
                    "class": "ptz",
                    "type": "is_moving",
                    "state": "0",
                    "tripped": False,
                },
        ),
        (
                PTZ_PRESET_INIT_1,
                {
                    "topic": "tns1:PTZController/tnsaxis:PTZPresets/Channel_1",
                    "source": "PresetToken",
                    "source_idx": "1",
                    "class": "ptz",
                    "type": "on_preset",
                    "state": "1",
                    "tripped": True,
                },
        ),
        (
                RELAY_INIT,
                {
                    "topic": "tns1:Device/Trigger/Relay",
                    "source": "RelayToken",
                    "source_idx": "3",
                    "class": "output",
                    "type": "Relay",
                    "state": "inactive",
                    "tripped": False,
                },
        ),
        (
                VMD3_INIT,
                {
                    "topic": "tns1:RuleEngine/tnsaxis:VMD3/vmd3_video_1",
                    "source": "areaid",
                    "source_idx": "0",
                    "class": "motion",
                    "type": "VMD3",
                    "state": "0",
                    "tripped": False,
                },
        ),
        (
                VMD4_ANY_INIT,
                {
                    "topic": "tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY",
                    "source": "",
                    "source_idx": "Camera1ProfileANY",
                    "class": "motion",
                    "type": "VMD4",
                    "state": "0",
                    "tripped": False,
                },
        ),
    ],
)
def test_create_event(event_manager, input: bytes, expected: tuple):
    """Verify that a new audio event can be managed."""
    event_manager.update(input)

    event = next(iter(event_manager.values()))
    assert event.topic == expected["topic"]
    assert event.source == expected["source"]
    assert event.id == expected["source_idx"]
    assert event.CLASS == expected["class"]
    assert event.TYPE == expected["type"]
    assert event.state == expected["state"]
    if event.BINARY:
        assert event.is_tripped is expected["tripped"]


@pytest.mark.parametrize("input", [[], [{"operation": "unsupported"}, {}]])
def test_do_not_create_event(event_manager, input: list):
    """Verify the different controls in pre_processed_raw."""
    event_manager.update(input)
    assert len(event_manager.values()) == 0


def test_vmd4_change(event_manager):
    """Verify that a VMD4 event change can be managed."""
    event_manager.update(VMD4_ANY_INIT)
    event_manager.update(VMD4_ANY_CHANGE)

    event = next(iter(event_manager.values()))
    assert event.state == "1"


def test_pir_init(event_manager):
    """Verify that a new PIR event can be managed."""
    event_manager.update(PIR_INIT)
    assert event_manager.values()

    event = next(iter(event_manager.values()))
    assert event.state == "0"
    assert not event.is_tripped

    mock_callback = Mock()
    event.register_callback(mock_callback)
    assert event.observers

    event_manager.update(PIR_CHANGE)
    assert event.state == "1"
    assert event.is_tripped
    assert mock_callback.called

    event.remove_callback(mock_callback)
    assert not event.observers


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


def test_unsupported_event(event_manager):
    """Verify that unsupported events aren't created."""
    event_manager.signal = Mock()
    event_manager.update(GLOBAL_SCENE_CHANGE)
    event_manager.signal.assert_not_called()

    event = next(iter(event_manager.values()))
    assert event.BINARY is False
    assert not event.TOPIC
    assert not event.CLASS
    assert not event.TYPE
    assert event.topic == "tns1:VideoSource/GlobalSceneChange/ImagingService"
    assert event.source == "Source"
    assert event.id == "0"
    assert event.state == "0"


def test_initialize_event_already_exist(event_manager):
    """Verify that initialize with an already existing event doesn't create."""
    event_manager.signal = Mock()
    event_manager.update(VMD4_ANY_INIT)
    assert len(event_manager.values()) == 1
    event_manager.signal.assert_called_once()

    event_manager.update(VMD4_ANY_INIT)
    assert len(event_manager.values()) == 1
    event_manager.signal.assert_called_once()
