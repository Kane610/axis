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
    zeroconf.zeroconf.async_wait_for_start = AsyncMock()
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
        {
            "host": host,
            "name": name,
            "macaddress": "00:40:8c:11:22:33",
            **({"link_local_host": "169.254.1.1"} if name == "B-dual" else {}),
        }
        for name, host in (
            ("B-dual", "192.0.2.40"),
            ("C-lan", "192.0.2.20"),
            ("A-link-local", "169.254.1.1"),
        )
    ]
    browser.async_cancel.assert_awaited_once()
    zeroconf.async_close.assert_awaited_once()


@pytest.mark.parametrize("during_request", [False, True])
async def test_removed_announcements_do_not_replace_fresh_data(
    during_request: bool,
) -> None:
    """A removed old name cannot hide a new name advertising the same device address."""
    zeroconf = MagicMock(async_close=AsyncMock())
    zeroconf.zeroconf.async_wait_for_start = AsyncMock()
    browser = MagicMock(async_cancel=AsyncMock())
    callback: Callable[..., None] | None = None
    old = f"A-old.{discovery.AXIS_SERVICE_TYPE}"
    fresh = f"Z-fresh.{discovery.AXIS_SERVICE_TYPE}"

    def announce(
        zc: object, service_types: list[str], handlers: list[Callable[..., None]]
    ) -> MagicMock:
        nonlocal callback
        callback = handlers[0]
        callback(zc, service_types[0], old, discovery.ServiceStateChange.Added)
        if not during_request:
            callback(zc, service_types[0], old, discovery.ServiceStateChange.Removed)
        callback(zc, service_types[0], fresh, discovery.ServiceStateChange.Updated)
        return browser

    def service_info(service_type: str, name: str) -> MagicMock:
        def resolve(zc: object, timeout: int) -> bool:
            if during_request and name == old:
                assert callback is not None
                callback(zc, service_type, old, discovery.ServiceStateChange.Removed)
            return True

        return MagicMock(
            async_request=AsyncMock(side_effect=resolve),
            properties={b"macaddress": b"00408C112233"},
            parsed_addresses=MagicMock(return_value=["192.0.2.1"]),
        )

    with (
        patch.object(discovery, "AsyncZeroconf", return_value=zeroconf),
        patch.object(discovery, "AsyncServiceBrowser", side_effect=announce),
        patch.object(discovery, "AsyncServiceInfo", side_effect=service_info),
        patch.object(discovery.asyncio, "sleep", new=AsyncMock()),
    ):
        assert await discovery.discover_axis_devices(0) == [
            {"name": "Z-fresh", "host": "192.0.2.1", "macaddress": "00408C112233"}
        ]


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


async def test_cancellation_during_zeroconf_startup_waits_for_cleanup() -> None:
    """Do not cancel Zeroconf's shared startup future before closing its sockets."""
    started, ready = asyncio.Event(), asyncio.Event()
    zeroconf = MagicMock(async_close=AsyncMock())

    async def start() -> None:
        started.set()
        await ready.wait()

    zeroconf.zeroconf.async_wait_for_start = AsyncMock(side_effect=start)
    with (
        patch.object(discovery, "AsyncZeroconf", return_value=zeroconf),
        patch.object(discovery, "AsyncServiceBrowser") as browser,
    ):
        task = asyncio.create_task(discovery.discover_axis_devices())
        await asyncio.wait_for(started.wait(), 2)
        task.cancel()
        ready.set()
        with pytest.raises(asyncio.CancelledError):
            await task
    browser.assert_not_called()
    zeroconf.async_close.assert_awaited_once()


async def test_streams_resolved_announcements_before_scan_ends() -> None:
    """Report a resolved device immediately and omit removed devices from the final list."""
    zeroconf = MagicMock(async_close=AsyncMock())
    zeroconf.zeroconf.async_wait_for_start = AsyncMock()
    browser = MagicMock(async_cancel=AsyncMock())
    browser_factory = MagicMock(return_value=browser)
    finish = asyncio.Event()
    started = asyncio.Event()

    async def scan_window(_duration: float) -> None:
        started.set()
        await finish.wait()

    published: asyncio.Queue[discovery.DiscoveredDevice] = asyncio.Queue()
    info = MagicMock(
        async_request=AsyncMock(return_value=True),
        properties={b"macaddress": b"00408C112233"},
        parsed_addresses=MagicMock(return_value=["192.0.2.1"]),
    )
    with (
        patch.object(discovery, "AsyncZeroconf", return_value=zeroconf),
        patch.object(discovery, "AsyncServiceBrowser", browser_factory),
        patch.object(discovery, "AsyncServiceInfo", return_value=info),
        patch.object(discovery.asyncio, "sleep", new=scan_window),
    ):
        async with asyncio.timeout(2), asyncio.TaskGroup() as group:
            scan = group.create_task(
                discovery.discover_axis_devices(on_device=published.put)
            )
            await started.wait()
            handler = browser_factory.call_args.kwargs["handlers"][0]
            service = discovery.AXIS_SERVICE_TYPE
            name = f"Entrance.{service}"
            handler(zeroconf, service, name, discovery.ServiceStateChange.Added)
            handler(zeroconf, service, name, discovery.ServiceStateChange.Updated)
            assert await published.get() == {
                "name": "Entrance",
                "host": "192.0.2.1",
                "macaddress": "00408C112233",
            }
            assert not scan.done()
            handler(zeroconf, service, name, discovery.ServiceStateChange.Removed)
            handler(
                zeroconf,
                service,
                f"Lobby.{service}",
                discovery.ServiceStateChange.Added,
            )
            lobby = await published.get()
            finish.set()
            assert await scan == [lobby]


@pytest.mark.parametrize("failure", ["construction", "cancellation", "cleanup"])
async def test_discovery_releases_resources_on_failure(failure: str) -> None:
    """Browser creation/cleanup failures and cancellation still close Zeroconf."""
    zeroconf = MagicMock(async_close=AsyncMock())
    zeroconf.zeroconf.async_wait_for_start = AsyncMock()
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
