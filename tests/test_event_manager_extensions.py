"""Tests for EventManager extension hooks."""

from axis.interfaces.event_manager import EventManager


def test_allowed_topics_filter_is_opt_in() -> None:
    """Allow-list should only apply when explicitly configured."""
    manager = EventManager()
    received = []
    manager.subscribe(lambda event: received.append(event.topic))

    pir_event = {
        "topic": "tns1:Device/tnsaxis:Sensor/PIR",
        "source": "sensor",
        "source_idx": "0",
        "type": "state",
        "value": "0",
        "operation": "Initialized",
    }
    light_event = {
        "topic": "tns1:Device/tnsaxis:Light/Status",
        "source": "id",
        "source_idx": "0",
        "type": "state",
        "value": "OFF",
        "operation": "Initialized",
    }

    manager.handler(pir_event)
    manager.handler(light_event)
    assert received == [
        "tns1:Device/tnsaxis:Sensor/PIR",
        "tns1:Device/tnsaxis:Light/Status",
    ]

    manager.set_allowed_topics(["tns1:Device/tnsaxis:Sensor/PIR"])
    manager.handler(light_event)
    assert received == [
        "tns1:Device/tnsaxis:Sensor/PIR",
        "tns1:Device/tnsaxis:Light/Status",
    ]
