"""Test discovery address selection, failure cleanup, and invalid scan rejection."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from axis.application import discovery
from axis.application.errors import ErrorKind, OperationError

if TYPE_CHECKING:
    from collections.abc import Callable


async def test_discovery_prefers_non_link_local_and_retains_fallbacks() -> None:
    """Prefer advertised LAN addresses before deduplication and list link-local fallbacks last."""
    advertisements = {
        "A-link-local": ["169.254.1.1"],
        "B-dual": ["169.254.1.1", "192.0.2.40", "192.0.2.41"],
        "C-lan": ["192.0.2.20", "192.0.2.21"],
        "D-duplicate": ["192.0.2.40"],
    }
    zeroconf = MagicMock(async_close=AsyncMock())
    browser = MagicMock(async_cancel=AsyncMock())

    def announce(
        zc: object, service_types: list[str], handlers: list[Callable[..., None]]
    ) -> MagicMock:
        for name in advertisements:
            handlers[0](
                zc,
                service_types[0],
                f"{name}.{discovery.AXIS_SERVICE_TYPE}",
                discovery.ServiceStateChange.Added,
            )
        return browser

    def service_info(service_type: str, name: str) -> MagicMock:
        instance = name.removesuffix(f".{service_type}")
        return MagicMock(
            async_request=AsyncMock(return_value=True),
            properties={b"macaddress": b"00:40:8c:11:22:33"},
            parsed_addresses=MagicMock(return_value=advertisements[instance]),
        )

    with (
        patch.object(discovery, "AsyncZeroconf", return_value=zeroconf),
        patch.object(discovery, "AsyncServiceBrowser", side_effect=announce),
        patch.object(discovery, "AsyncServiceInfo", side_effect=service_info),
        patch.object(discovery.asyncio, "sleep", new=AsyncMock()),
    ):
        results = await discovery.discover_axis_devices(0)
    assert results == [
        {"host": host, "name": name, "macaddress": "00:40:8c:11:22:33"}
        for name, host in (
            ("B-dual", "192.0.2.40"),
            ("C-lan", "192.0.2.20"),
            ("A-link-local", "169.254.1.1"),
        )
    ]
    browser.async_cancel.assert_awaited_once()
    zeroconf.async_close.assert_awaited_once()


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
