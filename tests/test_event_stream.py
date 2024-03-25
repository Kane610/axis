"""Test Axis event stream.

pytest --cov-report term-missing --cov=axis.event_stream tests/test_event_stream.py
"""

from unittest.mock import Mock

import pytest

from axis.device import AxisDevice
from axis.interfaces.event_manager import EventManager
from axis.models.event import Event, EventGroup, EventOperation, EventTopic

from .event_fixtures import (
    AUDIO_INIT,
    DAYNIGHT_INIT,
    FENCE_GUARD_INIT,
    GLOBAL_SCENE_CHANGE,
    LIGHT_STATUS_INIT,
    LOITERING_GUARD_INIT,
    MOTION_GUARD_INIT,
    OBJECT_ANALYTICS_INIT,
    PIR_CHANGE,
    PIR_INIT,
    PORT_0_INIT,
    PORT_ANY_INIT,
    PTZ_MOVE_END,
    PTZ_MOVE_INIT,
    PTZ_MOVE_START,
    PTZ_PRESET_AT_1_FALSE,
    PTZ_PRESET_AT_2_TRUE,
    PTZ_PRESET_INIT_1,
    PTZ_PRESET_INIT_2,
    PTZ_PRESET_INIT_3,
    RELAY_INIT,
    VMD3_INIT,
    VMD4_ANY_INIT,
    VMD4_C1P1_CHANGE,
    VMD4_C1P1_INIT,
    VMD4_C1P2_CHANGE,
    VMD4_C1P2_INIT,
)


@pytest.fixture
def event_manager(axis_device: AxisDevice) -> EventManager:
    """Return mocked event manager."""
    axis_device.enable_events()
    return axis_device.event


@pytest.fixture
def subscriber(event_manager: EventManager) -> Mock:
    """Return mocked event manager."""
    callback = Mock()
    event_manager.subscribe(callback)
    return callback


@pytest.mark.parametrize(
    ("input", "expected"),
    [
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
    ],
)
def test_create_event(
    event_manager: EventManager, subscriber: Mock, input: bytes, expected: tuple
) -> None:
    """Verify that a new audio event can be managed."""
    event_manager.handler(input)
    assert subscriber.call_count == 1

    event: Event = subscriber.call_args[0][0]
    assert event.topic == expected["topic"]
    assert event.source == expected["source"]
    assert event.id == expected["source_idx"]
    assert event.group == expected["group"]
    assert event.state == expected["state"]
    assert event.is_tripped is expected["tripped"]


def test_pir_init(event_manager: EventManager, subscriber: Mock) -> None:
    """Verify that a new PIR event can be managed."""
    event_manager.handler(PIR_INIT)
    assert subscriber.call_count == 1

    event: Event = subscriber.call_args[0][0]
    assert event.state == "0"
    assert not event.is_tripped

    event_manager.handler(PIR_CHANGE)
    event: Event = subscriber.call_args[0][0]
    assert event.state == "1"
    assert event.is_tripped


def test_ptz_preset(event_manager: EventManager, subscriber: Mock) -> None:
    """Verify that a new PTZ preset event can be managed."""
    event_manager.handler(PTZ_PRESET_INIT_1)
    assert subscriber.call_count == 1

    event: Event = subscriber.call_args[0][0]
    assert event.topic == "tns1:PTZController/tnsaxis:PTZPresets/Channel_1"
    assert event.id == "1"
    assert event.state == "1"

    event_manager.handler(PTZ_PRESET_INIT_2)
    assert subscriber.call_count == 2

    event: Event = subscriber.call_args[0][0]
    assert event.topic == "tns1:PTZController/tnsaxis:PTZPresets/Channel_1"
    assert event.id == "2"
    assert event.state == "0"

    event_manager.handler(PTZ_PRESET_INIT_3)
    assert subscriber.call_count == 3

    event: Event = subscriber.call_args[0][0]
    assert event.topic == "tns1:PTZController/tnsaxis:PTZPresets/Channel_1"
    assert event.id == "3"
    assert event.state == "0"

    event_manager.handler(PTZ_PRESET_AT_1_FALSE)
    assert subscriber.call_count == 4

    event: Event = subscriber.call_args[0][0]
    assert event.state == "0"
    assert not event.is_tripped

    event_manager.handler(PTZ_PRESET_AT_2_TRUE)
    assert subscriber.call_count == 5

    event: Event = subscriber.call_args[0][0]
    assert event.state == "1"
    assert event.is_tripped


def test_ptz_move(event_manager: EventManager, subscriber: Mock) -> None:
    """Verify that a new PTZ move event can be managed."""
    event_manager.handler(PTZ_MOVE_INIT)
    assert subscriber.call_count == 1

    event: Event = subscriber.call_args[0][0]
    assert event.topic == "tns1:PTZController/tnsaxis:Move/Channel_1"
    assert event.source == "PTZConfigurationToken"
    assert event.id == "1"
    assert event.group == EventGroup.PTZ
    assert event.state == "0"

    event_manager.handler(PTZ_MOVE_START)
    assert subscriber.call_count == 2

    event: Event = subscriber.call_args[0][0]
    assert event.topic == "tns1:PTZController/tnsaxis:Move/Channel_1"
    assert event.id == "1"
    assert event.state == "1"
    assert event.is_tripped

    event_manager.handler(PTZ_MOVE_END)
    assert subscriber.call_count == 3

    event: Event = subscriber.call_args[0][0]
    assert event.topic == "tns1:PTZController/tnsaxis:Move/Channel_1"
    assert event.id == "1"
    assert event.state == "0"
    assert not event.is_tripped


def test_mqtt_event(event_manager: EventManager, subscriber: Mock) -> None:
    """Verify that unsupported events aren't signalled to subscribers."""
    mqtt_event = {
        "topic": "tns1:Device/tnsaxis:Sensor/PIR",
        "source": "sensor",
        "source_idx": "0",
        "type": "state",
        "value": "0",
    }
    event_manager.handler(mqtt_event)
    assert subscriber.call_count == 1

    event: Event = subscriber.call_args[0][0]
    assert event.operation == EventOperation.INITIALIZED
    assert event.topic == "tns1:Device/tnsaxis:Sensor/PIR"
    assert event.id == "0"
    assert event.state == "0"
    assert not event.is_tripped

    mqtt_event["value"] = "1"
    event_manager.handler(mqtt_event)
    assert subscriber.call_count == 2

    event: Event = subscriber.call_args[0][0]
    assert event.operation == EventOperation.CHANGED
    assert event.state == "1"
    assert event.is_tripped


def test_unsupported_event(event_manager: EventManager, subscriber: Mock) -> None:
    """Verify that unsupported events aren't signalled to subscribers."""
    event_manager.handler(GLOBAL_SCENE_CHANGE)
    subscriber.assert_not_called()


def test_initialize_event_twice(event_manager: EventManager, subscriber: Mock) -> None:
    """Verify that initialize with an already existing event doesn't create."""
    event_manager.handler(VMD4_ANY_INIT)
    assert subscriber.call_count == 1

    event_manager.handler(VMD4_ANY_INIT)
    assert subscriber.call_count == 2


def test_subscription(event_manager: EventManager) -> None:
    """Validate subscription mechanisms work."""
    subscriber_any = Mock()
    subscriber_vmd4 = Mock()
    subscriber_vmd4_c1p1 = Mock()
    subscriber_vmd4_c1p2 = Mock()

    unsub_any = event_manager.subscribe(subscriber_any)
    assert len(event_manager) == 1

    unsub_vmd4 = event_manager.subscribe(
        subscriber_vmd4,
        topic_filter=EventTopic.MOTION_DETECTION_4,
    )
    assert len(event_manager) == 2

    unsub_vmd4_c1p1 = event_manager.subscribe(
        subscriber_vmd4_c1p1,
        id_filter="Camera1Profile1",
        topic_filter=EventTopic.MOTION_DETECTION_4,
        operation_filter=EventOperation.INITIALIZED,
    )
    assert len(event_manager) == 3

    unsub_vmd4_c1p2 = event_manager.subscribe(
        subscriber_vmd4_c1p2,
        id_filter=("Camera1Profile2",),
        topic_filter=(EventTopic.MOTION_DETECTION_4,),
        operation_filter=(EventOperation.INITIALIZED, EventOperation.CHANGED),
    )
    assert len(event_manager) == 4

    # Validate subscription matching
    event_manager.handler(PIR_INIT)
    assert subscriber_any.call_count == 1
    assert subscriber_vmd4.call_count == 0
    assert subscriber_vmd4_c1p1.call_count == 0
    assert subscriber_vmd4_c1p2.call_count == 0

    event_manager.handler(VMD4_C1P1_INIT)
    assert subscriber_any.call_count == 2
    assert subscriber_vmd4.call_count == 1
    assert subscriber_vmd4_c1p1.call_count == 1
    assert subscriber_vmd4_c1p2.call_count == 0

    event_manager.handler(VMD4_C1P2_INIT)
    assert subscriber_any.call_count == 3
    assert subscriber_vmd4.call_count == 2
    assert subscriber_vmd4_c1p1.call_count == 1
    assert subscriber_vmd4_c1p2.call_count == 1

    event_manager.handler(VMD4_C1P1_CHANGE)
    assert subscriber_any.call_count == 4
    assert subscriber_vmd4.call_count == 3
    assert subscriber_vmd4_c1p1.call_count == 1
    assert subscriber_vmd4_c1p2.call_count == 1

    event_manager.handler(VMD4_C1P2_CHANGE)
    assert subscriber_any.call_count == 5
    assert subscriber_vmd4.call_count == 4
    assert subscriber_vmd4_c1p1.call_count == 1
    assert subscriber_vmd4_c1p2.call_count == 2

    # validate unsubscribing
    unsub_any()
    assert len(event_manager) == 3
    unsub_vmd4()
    assert len(event_manager) == 2
    unsub_vmd4_c1p1()
    assert len(event_manager) == 1
    unsub_vmd4_c1p2()
    assert len(event_manager) == 0

    # Validate no exception when unsubscribe with no subscription exist
    unsub_any()

    # Validate no exception when unsubscribe with no object ID exist
    event_manager._subscribers.pop("Camera1Profile1")
    unsub_vmd4_c1p1()
