"""Discovery lifecycle faults that must not leak resources or emit false success."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from axis.application import discovery
from axis.application.errors import ErrorKind, OperationError


@pytest.mark.parametrize("duration", [-1.0, float("inf"), float("nan")])
async def test_invalid_duration_is_offline(duration: float) -> None:
    """Unbounded or invalid scan durations fail before creating network resources."""
    with (
        patch.object(discovery, "AsyncZeroconf") as create,
        pytest.raises(OperationError) as caught,
    ):
        await discovery.discover_axis_devices(duration)
    assert caught.value.kind is ErrorKind.VALIDATION
    create.assert_not_called()


@pytest.mark.parametrize("failure", ["construction", "cancellation", "cleanup"])
async def test_discovery_releases_resources_on_failure(failure: str) -> None:
    """Browser creation/cleanup failures and cancellation still close Zeroconf."""
    zeroconf = MagicMock(async_close=AsyncMock())
    browser = MagicMock(async_cancel=AsyncMock())
    create_browser = MagicMock(return_value=browser)
    sleep = AsyncMock()
    if failure == "construction":
        create_browser.side_effect = RuntimeError("secret")
    elif failure == "cancellation":
        sleep.side_effect = asyncio.CancelledError
    else:
        browser.async_cancel.side_effect = RuntimeError("secret")
    with (
        patch.object(discovery, "AsyncZeroconf", return_value=zeroconf),
        patch.object(discovery, "AsyncServiceBrowser", create_browser),
        patch.object(discovery.asyncio, "sleep", sleep),
        pytest.raises(
            asyncio.CancelledError if failure == "cancellation" else OperationError
        ) as caught,
    ):
        await discovery.discover_axis_devices(0)
    zeroconf.async_close.assert_awaited_once()
    if failure != "construction":
        browser.async_cancel.assert_awaited_once()
    assert "secret" not in str(caught.value)
