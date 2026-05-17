"""Tests for EventTopicFilter value object.

pytest --cov-report term-missing --cov=axis.models.events.topic_filter tests/test_event_topic_filter.py
"""

import pytest

from axis.models.events.event import EventTopic
from axis.models.events.subscription_contracts import DesiredEventSubscription
from axis.models.events.topic_filter import EventTopicFilter, from_desired_subscriptions


class TestForAllEvents:
    """Tests for EventTopicFilter.for_all_events()."""

    def test_is_wildcard(self) -> None:
        """for_all_events() produces a wildcard filter."""
        f = EventTopicFilter.for_all_events()
        assert f.is_wildcard is True

    def test_canonical_topics_empty(self) -> None:
        """Wildcard returns empty canonical_topics list."""
        f = EventTopicFilter.for_all_events()
        assert f.canonical_topics == []

    def test_mqtt_topic_filters_empty(self) -> None:
        """Wildcard returns empty mqtt_topic_filters list."""
        f = EventTopicFilter.for_all_events()
        assert f.mqtt_topic_filters == []

    def test_equality(self) -> None:
        """Two wildcard instances are equal."""
        assert EventTopicFilter.for_all_events() == EventTopicFilter.for_all_events()

    def test_hashable(self) -> None:
        """Wildcard filter is hashable (frozen dataclass)."""
        f = EventTopicFilter.for_all_events()
        assert hash(f) == hash(EventTopicFilter.for_all_events())


class TestFromTopics:
    """Tests for EventTopicFilter.from_topics()."""

    def test_empty_raises(self) -> None:
        """from_topics([]) raises ValueError."""
        with pytest.raises(ValueError, match="topics must not be empty"):
            EventTopicFilter.from_topics([])

    def test_canonical_string_stored_as_is(self) -> None:
        """Canonical-format strings are stored without conversion."""
        topic = "tns1:Device/tnsaxis:Sensor/PIR"
        f = EventTopicFilter.from_topics([topic])
        assert f.canonical_topics == [topic]

    def test_mqtt_string_converted_to_canonical(self) -> None:
        """MQTT-format strings are converted to canonical."""
        f = EventTopicFilter.from_topics(["onvif:Device/axis:Sensor/PIR"])
        assert f.canonical_topics == ["tns1:Device/tnsaxis:Sensor/PIR"]

    def test_event_topic_enum(self) -> None:
        """EventTopic enum values are accepted and stored as canonical."""
        f = EventTopicFilter.from_topics([EventTopic.PIR])
        assert f.canonical_topics == [EventTopic.PIR.value]

    def test_mixed_input(self) -> None:
        """Mixed str and EventTopic inputs are normalized together."""
        f = EventTopicFilter.from_topics([EventTopic.PIR, "onvif:Device/axis:IO/Port"])
        assert f.canonical_topics == [
            "tns1:Device/tnsaxis:IO/Port",
            "tns1:Device/tnsaxis:Sensor/PIR",
        ]

    def test_is_not_wildcard(self) -> None:
        """from_topics() result is never a wildcard."""
        f = EventTopicFilter.from_topics(["tns1:Device/tnsaxis:Sensor/PIR"])
        assert f.is_wildcard is False

    def test_deduplication(self) -> None:
        """Duplicate topics (after normalization) are deduplicated."""
        f = EventTopicFilter.from_topics(
            [
                "tns1:Device/tnsaxis:Sensor/PIR",
                "onvif:Device/axis:Sensor/PIR",  # same as above in MQTT form
            ]
        )
        assert f.canonical_topics == ["tns1:Device/tnsaxis:Sensor/PIR"]

    def test_sorted_output(self) -> None:
        """canonical_topics and mqtt_topic_filters return sorted lists."""
        f = EventTopicFilter.from_topics(
            [
                "tns1:Device/tnsaxis:Sensor/PIR",
                "tns1:Device/tnsaxis:IO/Port",
            ]
        )
        assert f.canonical_topics == [
            "tns1:Device/tnsaxis:IO/Port",
            "tns1:Device/tnsaxis:Sensor/PIR",
        ]
        assert f.mqtt_topic_filters == [
            "onvif:Device/axis:IO/Port",
            "onvif:Device/axis:Sensor/PIR",
        ]

    def test_mqtt_topic_filters_conversion(self) -> None:
        """mqtt_topic_filters returns MQTT-format strings."""
        f = EventTopicFilter.from_topics(["tns1:Device/tnsaxis:Sensor/PIR"])
        assert f.mqtt_topic_filters == ["onvif:Device/axis:Sensor/PIR"]

    def test_immutable(self) -> None:
        """EventTopicFilter is immutable (frozen dataclass)."""
        f = EventTopicFilter.from_topics(["tns1:Device/tnsaxis:Sensor/PIR"])
        with pytest.raises(AttributeError):
            f._topics = frozenset()  # type: ignore[misc]

    def test_equality(self) -> None:
        """Two filters with the same topics are equal."""
        f1 = EventTopicFilter.from_topics(["tns1:Device/tnsaxis:Sensor/PIR"])
        f2 = EventTopicFilter.from_topics(["onvif:Device/axis:Sensor/PIR"])
        assert f1 == f2

    def test_hashable(self) -> None:
        """from_topics result is hashable."""
        f = EventTopicFilter.from_topics(["tns1:Device/tnsaxis:Sensor/PIR"])
        assert isinstance(hash(f), int)


class TestFromDesiredSubscriptions:
    """Tests for the from_desired_subscriptions() compat helper."""

    def test_builds_from_desired_subscriptions(self) -> None:
        """from_desired_subscriptions bridges DesiredEventSubscription objects."""
        subscriptions = [
            DesiredEventSubscription(topic="onvif:Device/axis:Sensor/PIR"),
            DesiredEventSubscription(topic="tns1:Device/tnsaxis:IO/Port"),
        ]
        f = from_desired_subscriptions(subscriptions)
        assert f.canonical_topics == [
            "tns1:Device/tnsaxis:IO/Port",
            "tns1:Device/tnsaxis:Sensor/PIR",
        ]

    def test_empty_raises(self) -> None:
        """Empty subscriptions list raises ValueError."""
        with pytest.raises(ValueError, match="topics must not be empty"):
            from_desired_subscriptions([])
