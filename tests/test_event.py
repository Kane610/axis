"""Test Axis event class.

pytest --cov-report term-missing --cov=axis.models.event tests/test_event.py
"""

from unittest.mock import patch

import pytest

from axis.models.event import Event, EventGroup, EventOperation

from .event_fixtures import (
    AUDIO_INIT,
    DAYNIGHT_INIT,
    FENCE_GUARD_INIT,
    FIRST_MESSAGE,
    GLOBAL_SCENE_CHANGE,
    LIGHT_STATUS_INIT,
    LOITERING_GUARD_INIT,
    MOTION_GUARD_INIT,
    OBJECT_ANALYTICS_INIT,
    PIR_CHANGE,
    PIR_INIT,
    PORT_0_INIT,
    PORT_ANY_INIT,
    PTZ_MOVE_INIT,
    PTZ_PRESET_INIT_1,
    RELAY_INIT,
    RULE_ENGINE_REGION_DETECTOR_INIT,
    STORAGE_ALERT_INIT,
    VMD3_INIT,
    VMD4_ANY_CHANGE,
    VMD4_ANY_INIT,
)


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        (
            FIRST_MESSAGE,
            {
                "topic": "",
                "source": "",
                "source_idx": "",
                "group": EventGroup.NONE,
                "type": "",
                "state": "",
                "tripped": False,
            },
        ),
        (
            AUDIO_INIT,
            {
                "topic": "tns1:AudioSource/tnsaxis:TriggerLevel",
                "source": "channel",
                "source_idx": "1",
                "group": EventGroup.SOUND,
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
                "group": EventGroup.LIGHT,
                "type": "DayNight",
                "state": "1",
                "tripped": True,
            },
        ),
        (
            FENCE_GUARD_INIT,
            {
                "topic": "tnsaxis:CameraApplicationPlatform/FenceGuard/Camera1Profile1",
                "source": "",
                "source_idx": "Camera1Profile1",
                "group": EventGroup.MOTION,
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
                "group": EventGroup.LIGHT,
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
                "group": EventGroup.MOTION,
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
                "group": EventGroup.MOTION,
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
                "group": EventGroup.MOTION,
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
                "group": EventGroup.MOTION,
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
                "group": EventGroup.INPUT,
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
                "group": EventGroup.INPUT,
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
                "group": EventGroup.PTZ,
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
                "group": EventGroup.PTZ,
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
                "group": EventGroup.OUTPUT,
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
                "group": EventGroup.MOTION,
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
                "group": EventGroup.MOTION,
                "type": "VMD4",
                "state": "0",
                "tripped": False,
            },
        ),
        # Unsupported event
        (
            GLOBAL_SCENE_CHANGE,
            {
                "topic": "tns1:VideoSource/GlobalSceneChange/ImagingService",
                "source": "Source",
                "source_idx": "0",
                "group": EventGroup.NONE,
                "type": "VMD4",
                "state": "0",
                "tripped": False,
            },
        ),
    ],
)
def test_create_event(input: bytes, expected: tuple) -> None:
    """Verify that a new audio event can be managed."""
    event = Event.decode(input)

    assert event.topic == expected["topic"]
    assert event.source == expected["source"]
    assert event.id == expected["source_idx"]
    assert event.group == expected["group"]
    assert event.state == expected["state"]
    assert event.is_tripped is expected["tripped"]


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        (
            FIRST_MESSAGE,
            {},
        ),
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
                "source": "",
                "source_idx": "",
                "type": "active",
                "value": "0",
            },
        ),
        (
            VMD4_ANY_CHANGE,
            {
                "operation": "Changed",
                "topic": "tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY",
                "source": "",
                "source_idx": "",
                "type": "active",
                "value": "1",
            },
        ),
    ],
)
def test_parse_event_xml(input: bytes, expected: dict):
    """Verify parse_event_xml output."""
    with patch.object(Event, "_decode_from_dict") as mock_decode_from_dict:
        assert Event.decode(input)
        assert mock_decode_from_dict.call_args[0][0] == expected


def test_unknown_event_operation():
    """Verify unknown event operation is caught."""
    assert EventOperation("") == EventOperation.UNKNOWN
