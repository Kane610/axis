"""Validate API handler and its subsription handling."""
from unittest.mock import Mock

from axis.vapix.interfaces.api_handler import SubscriptionHandler


class ClassForTest(SubscriptionHandler):
    """Class to test subscriptions."""


def test_no_subscribers() -> None:
    """Check data on no subscribers."""
    test_class = ClassForTest()

    assert len(test_class._subscribers) == 1

    callback = Mock()
    test_class.signal_subscribers("1")
    callback.assert_not_called()


def test_all_filter_subscribers() -> None:
    """Validate signalling a ID all subscriber."""
    test_class = ClassForTest()

    assert len(test_class._subscribers) == 1
    unsub = test_class.subscribe(callback := Mock())
    assert len(test_class._subscribers) == 1

    test_class.signal_subscribers("1")
    callback.assert_called_once_with("1")

    test_class.signal_subscribers("2")
    callback.assert_called_with("2")

    unsub()


def test_id_1_filter_subscribers() -> None:
    """Validate signalling one subscriber."""
    test_class = ClassForTest()

    assert len(test_class._subscribers) == 1
    test_class.subscribe(callback := Mock(), "1")
    assert len(test_class._subscribers) == 2

    test_class.signal_subscribers("1")
    callback.assert_called_once_with("1")

    test_class.signal_subscribers("2")
    callback.assert_called_once_with("1")


def test_multiple_subscribers() -> None:
    """Validate signalling multiple subscribers."""
    test_class = ClassForTest()

    assert len(test_class._subscribers) == 1
    test_class.subscribe(callback := Mock(), "1")
    assert len(test_class._subscribers) == 2
    test_class.subscribe(callback2 := Mock())
    assert len(test_class._subscribers) == 2

    test_class.signal_subscribers("1")
    callback.assert_called_with("1")

    test_class.signal_subscribers("2")
    callback2.assert_called_with("2")


def test_unsub_missing_obj_id() -> None:
    """Validate nothing breaks on unsub with missing object id."""
    test_class = ClassForTest()
    unsub = test_class.subscribe(Mock())
    test_class._subscribers.clear()
    unsub()


def test_unsub_missing_subscription() -> None:
    """Validate nothing breaks on unsub with missing subscription."""
    test_class = ClassForTest()
    unsub = test_class.subscribe(Mock())
    test_class._subscribers["*"].clear()
    unsub()
