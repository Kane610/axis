"""Test Axis event class.

pytest --cov-report term-missing --cov=axis.models.event tests/test_event.py
"""

from unittest.mock import patch

import pytest

from axis.models.event import (
    Event,
    EventOperation,
    EventTopic,
    extract_name_value,
    traverse,
)

from .event_fixtures import (
    AUDIO_INIT,
    DAYNIGHT_INIT,
    FENCE_GUARD_INIT,
    FIRST_MESSAGE,
    GLOBAL_SCENE_CHANGE,
    LIGHT_STATUS_INIT,
    LOITERING_GUARD_INIT,
    MOTION_GUARD_INIT,
    OBJECT_ANALYTICS_ANY_CHANGE,
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
                "type": "Object Analytics",
                "state": "0",
                "tripped": False,
            },
        ),
        (
            OBJECT_ANALYTICS_ANY_CHANGE,
            {
                "topic": "tnsaxis:CameraApplicationPlatform/ObjectAnalytics/Device1Scenario1",
                "source": "",
                "source_idx": "Device1Scenario1",
                "type": "Object Analytics",
                "state": "1",
                "tripped": True,
            },
        ),
        (
            PIR_INIT,
            {
                "topic": "tns1:Device/tnsaxis:Sensor/PIR",
                "source": "sensor",
                "source_idx": "0",
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
        (
            OBJECT_ANALYTICS_ANY_CHANGE,
            {
                "operation": "Changed",
                "topic": "tnsaxis:CameraApplicationPlatform/ObjectAnalytics/Device1Scenario1",
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


@pytest.mark.parametrize(
    ("event_data", "expected"),
    [
        (
            {
                "topic": "tnsaxis:CameraApplicationPlatform/ObjectAnalytics/Device1Scenario1",
                "source": "",
                "source_idx": "Device1Scenario1",
                "type": "active",
                "value": "0",
            },
            False,
        ),
        (
            {
                "topic": "tnsaxis:CameraApplicationPlatform/ObjectAnalytics/Device1Scenario1",
                "source": "",
                "source_idx": "Device1Scenario1",
                "type": "classType",
                "value": "human",
            },
            True,
        ),
        (
            {
                "topic": "tns1:Device/tnsaxis:Sensor/PIR",
                "source": "sensor",
                "source_idx": "0",
                "type": "state",
                "value": "0",
            },
            False,
        ),
        (
            {
                "topic": "tns1:AudioSource/tnsaxis:TriggerLevel",
                "source": "channel",
                "source_idx": "1",
                "type": "active",
                "value": "high",
            },
            True,
        ),
        (
            {
                "topic": "tns1:AudioSource/tnsaxis:TriggerLevel",
                "source": "channel",
                "source_idx": "1",
                "type": "active",
                "value": "unknown",
            },
            False,
        ),
        (
            {
                "topic": "tnsaxis:CameraApplicationPlatform/ObjectAnalytics/Device1Scenario1",
                "source": "",
                "source_idx": "Device1Scenario1",
                "type": "classType",
                "value": "   ",
            },
            False,
        ),
    ],
)
def test_decode_from_dict_type_aware_is_tripped(
    event_data: dict[str, str], expected: bool
) -> None:
    """Verify state handling for binary and semantic event payloads."""
    event = Event.decode(event_data)

    assert event.is_tripped is expected


def test_decode_from_dict_resolves_topic_suffix_without_warning(caplog) -> None:
    """Verify recoverable topics do not produce unsupported-topic warnings."""
    event_data = {
        "topic": "tnsaxis:CameraApplicationPlatform/VMD/Camera1Profile1",
        "source": "",
        "source_idx": "",
        "type": "active",
        "value": "0",
    }

    with caplog.at_level("WARNING"):
        event = Event.decode(event_data)

    assert event.topic_base == EventTopic.MOTION_DETECTION_4
    assert event.id == "Camera1Profile1"
    assert "Unsupported topic" not in caplog.text


def test_traverse_non_dict_data():
    """Test traverse function with non-dict data returns empty dict."""
    # Passing non-dict should return empty dict
    result = traverse(None, ("key",))
    assert result == {}

    result = traverse("not a dict", ("key",))
    assert result == {}

    result = traverse([], ("key",))
    assert result == {}


def test_extract_name_value_empty_list():
    """Test extract_name_value with empty SimpleItem list."""
    # Empty list should return empty strings
    data = {"SimpleItem": []}
    name, value = extract_name_value(data)
    assert name == ""
    assert value == ""


def test_extract_name_value_with_prefer():
    """Test extract_name_value with prefer parameter finds matching item."""
    # Test with prefer parameter that matches an item
    data = {
        "SimpleItem": [
            {"Name": "State", "Value": "0"},
            {"Name": "active", "Value": "1"},
            {"Name": "Other", "Value": "2"},
        ]
    }
    name, value = extract_name_value(data, prefer="active")
    assert name == "active"
    assert value == "1"

    # Test with prefer parameter that doesn't match (falls back to first item)
    name, value = extract_name_value(data, prefer="nonexistent")
    assert name == "State"
    assert value == "0"
