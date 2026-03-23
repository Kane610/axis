"""Validate API handler and its subsription handling."""

from unittest.mock import MagicMock, Mock

import pytest

from axis.interfaces.api_handler import ApiHandler, HandlerGroup, SubscriptionHandler
from axis.interfaces.light_control import LightHandler


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


def test_api_version_always_returns_string() -> None:
    """Verify api_version property always returns str, never None.

    This is a contract guarantee: even handlers without discovery
    or default_api_version must return a string.
    """
    # Create a minimal handler without discovery data
    handler = ApiHandler(vapix=MagicMock())
    handler.api_id = None  # No discovery for this handler
    handler.default_api_version = None  # No default set

    # Property must ALWAYS return a string, never None
    version = handler.api_version
    assert isinstance(version, str), "api_version must always be a string"
    assert version == "", "Handlers without api_id/default return empty string"


def test_api_version_with_default() -> None:
    """Verify api_version returns default_api_version when available."""
    handler = ApiHandler(vapix=MagicMock())
    handler.api_id = None
    handler.default_api_version = "1.0"

    version = handler.api_version
    assert version == "1.0", "Should return default_api_version when set"


def test_api_version_discovery_precedence() -> None:
    """Verify discovery version takes precedence over default."""
    # Mock discovery with a version
    vapix = MagicMock()
    vapix.api_discovery.get.return_value.version = "2.0"

    handler = ApiHandler(vapix=vapix)
    handler.api_id = "test_id"
    handler.default_api_version = "1.0"

    version = handler.api_version
    assert version == "2.0", "Discovery version should take precedence over default"


def test_api_version_discovery_empty_string_precedence() -> None:
    """Verify empty discovery version is still preferred over default."""
    vapix = MagicMock()
    vapix.api_discovery.get.return_value.version = ""

    handler = ApiHandler(vapix=vapix)
    handler.api_id = "test_id"
    handler.default_api_version = "1.0"

    version = handler.api_version
    assert version == "", "Discovery version should be used even when empty"


def test_should_initialize_in_group_default_true() -> None:
    """Verify default initialization policy allows all groups."""
    handler = ApiHandler(vapix=MagicMock())

    assert handler.should_initialize_in_group(HandlerGroup.API_DISCOVERY)
    assert handler.should_initialize_in_group(HandlerGroup.PARAM_CGI_FALLBACK)
    assert handler.should_initialize_in_group(HandlerGroup.APPLICATION)


def test_initialization_groups_returns_handler_groups() -> None:
    """Verify initialization_groups is sourced from handler_groups."""
    handler = ApiHandler(vapix=MagicMock())

    assert handler.initialization_groups == ()

    handler.handler_groups = (
        HandlerGroup.API_DISCOVERY,
        HandlerGroup.PARAM_CGI_FALLBACK,
    )
    assert handler.initialization_groups == (
        HandlerGroup.API_DISCOVERY,
        HandlerGroup.PARAM_CGI_FALLBACK,
    )


def test_light_handler_param_fallback_policy() -> None:
    """Verify light handler fallback policy is owned by the handler."""
    vapix = MagicMock()
    handler = LightHandler(vapix=vapix)

    # Supported via params and not API discovery -> should initialize in fallback
    vapix.params.property_handler.get.return_value.light_control = True
    vapix.api_discovery.__contains__.return_value = False
    assert handler.should_initialize_in_group(HandlerGroup.PARAM_CGI_FALLBACK)

    # Supported via API discovery -> should not initialize in fallback
    vapix.api_discovery.__contains__.return_value = True
    assert not handler.should_initialize_in_group(HandlerGroup.PARAM_CGI_FALLBACK)
