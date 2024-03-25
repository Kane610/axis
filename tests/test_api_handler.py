"""Validate API handler and its subsription handling."""

from unittest.mock import Mock

import pytest

from axis.interfaces.api_handler import SubscriptionHandler


@pytest.fixture
def test_class():
    """Fixture creating class for testing."""

    class ClassForTest(SubscriptionHandler):
        """Class to test subscriptions."""

    return ClassForTest()


def test_no_subscribers(test_class) -> None:
    """Check data on no subscribers."""
    assert len(test_class._subscribers) == 1

    callback = Mock()
    test_class.signal_subscribers("1")
    callback.assert_not_called()


def test_all_filter_subscribers(test_class) -> None:
    """Validate signalling a ID all subscriber."""
    assert len(test_class._subscribers) == 1
    unsub = test_class.subscribe(callback := Mock())
    assert len(test_class._subscribers) == 1

    test_class.signal_subscribers("1")
    callback.assert_called_once_with("1")

    test_class.signal_subscribers("2")
    callback.assert_called_with("2")

    unsub()


def test_id_1_filter_subscribers(test_class) -> None:
    """Validate signalling one subscriber."""
    assert len(test_class._subscribers) == 1
    test_class.subscribe(callback := Mock(), "1")
    assert len(test_class._subscribers) == 2

    test_class.signal_subscribers("1")
    callback.assert_called_once_with("1")

    test_class.signal_subscribers("2")
    callback.assert_called_once_with("1")


def test_multiple_subscribers(test_class) -> None:
    """Validate signalling multiple subscribers."""
    assert len(test_class._subscribers) == 1
    test_class.subscribe(callback := Mock(), "1")
    assert len(test_class._subscribers) == 2
    test_class.subscribe(callback2 := Mock())
    assert len(test_class._subscribers) == 2

    test_class.signal_subscribers("1")
    callback.assert_called_with("1")

    test_class.signal_subscribers("2")
    callback2.assert_called_with("2")


def test_unsub_missing_obj_id(test_class) -> None:
    """Validate nothing breaks on unsub with missing object id."""
    unsub = test_class.subscribe(Mock())
    test_class._subscribers.clear()
    unsub()


def test_unsub_missing_subscription(test_class) -> None:
    """Validate nothing breaks on unsub with missing subscription."""
    unsub = test_class.subscribe(Mock())
    test_class._subscribers["*"].clear()
    unsub()
