"""Test CLI HTTP client backend selection."""

import asyncio
import logging
from pathlib import Path
import runpy
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from axis.__main__ import (
    axis_device,
    close_session,
    create_session,
    event_handler,
    main,
    websocket_flags_from_mode,
)
from axis.errors import AxisException, RequestError, Unauthorized
from axis.models.configuration import WebProtocol


async def test_create_session_aiohttp() -> None:
    """Verify session creation returns an aiohttp ClientSession."""
    session = create_session()

    try:
        assert isinstance(session, aiohttp.ClientSession)
    finally:
        await close_session(session)


async def test_close_session_aiohttp() -> None:
    """Verify close_session closes aiohttp sessions."""
    session = aiohttp.ClientSession()
    await close_session(session)
    assert session.closed


@pytest.mark.parametrize(
    ("stream_mode", "expected"),
    [
        ("rtsp", (False, False)),
        ("auto", (True, False)),
        ("event", (True, True)),
        ("unknown", (False, False)),
    ],
)
def test_websocket_flags_from_mode(
    stream_mode: str, expected: tuple[bool, bool]
) -> None:
    """Verify CLI stream mode mapping to websocket flags."""
    assert websocket_flags_from_mode(stream_mode) == expected


async def test_axis_device_initializes_and_configures_stream_mode(session) -> None:
    """Initialize device users and map the requested stream mode into config."""
    device = MagicMock()
    device.vapix.initialize_users = AsyncMock()
    device.vapix.load_user_groups = AsyncMock()
    with (
        patch("axis.__main__.create_session", return_value=session),
        patch("axis.__main__.AxisDevice", return_value=device) as device_factory,
    ):
        result = await axis_device(
            "camera.local",
            443,
            "root",
            "secret",
            WebProtocol.HTTPS,
            stream_mode="event",
            is_companion=True,
        )

    assert result is device
    device.vapix.initialize_users.assert_awaited_once()
    device.vapix.load_user_groups.assert_awaited_once()
    config = device_factory.call_args.args[0]
    assert config.websocket_enabled is True
    assert config.websocket_force is True
    assert config.is_companion is True


@pytest.mark.parametrize(
    ("error", "log_level", "log_message"),
    [
        (Unauthorized("denied"), "WARNING", "not registered"),
        (TimeoutError(), "ERROR", "Error connecting"),
        (RequestError("offline"), "ERROR", "Error connecting"),
        (AxisException("unknown"), "ERROR", "Unknown Axis communication error"),
    ],
)
async def test_axis_device_handles_initialization_failures(
    session,
    caplog: pytest.LogCaptureFixture,
    error: Exception,
    log_level: str,
    log_message: str,
) -> None:
    """Log expected authentication, connection, timeout, and Axis errors."""
    device = MagicMock()
    device.vapix.initialize_users = AsyncMock(side_effect=error)
    device.vapix.load_user_groups = AsyncMock()
    with (
        patch("axis.__main__.create_session", return_value=session),
        patch("axis.__main__.AxisDevice", return_value=device),
        caplog.at_level(log_level, logger="axis.__main__"),
    ):
        result = await axis_device(
            "camera.local", 80, "root", "secret", WebProtocol.HTTP
        )

    assert result is device
    assert log_message in caplog.text
    device.vapix.load_user_groups.assert_not_awaited()


async def test_main_returns_when_device_creation_fails(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Skip initialization and cleanup when no device can be created."""
    with (
        patch("axis.__main__.axis_device", new=AsyncMock(return_value=None)),
        caplog.at_level(logging.ERROR, logger="axis.__main__"),
    ):
        await main(
            "camera.local",
            80,
            "root",
            "secret",
            params=False,
            events=False,
            web_proto=WebProtocol.HTTP,
            stream_mode="rtsp",
        )

    assert "Couldn't connect to Axis device" in caplog.text


async def test_main_initializes_params_and_closes_session() -> None:
    """Initialize requested params and always close the HTTP session."""
    device = MagicMock()
    device.vapix.initialize = AsyncMock()
    device.stream.stop = MagicMock()
    device.config.session = MagicMock()

    with (
        patch("axis.__main__.axis_device", new=AsyncMock(return_value=device)),
        patch("axis.__main__.close_session", new=AsyncMock()) as close,
    ):
        await main(
            "camera.local",
            80,
            "root",
            "secret",
            params=True,
            events=False,
            web_proto=WebProtocol.HTTP,
            stream_mode="rtsp",
        )

    device.vapix.initialize.assert_awaited_once()
    close.assert_awaited_once_with(device.config.session)
    device.stream.stop.assert_called_once()


async def test_main_cancels_event_wait_and_stops_stream() -> None:
    """Stop event streaming on cancellation and still close the session."""
    device = MagicMock()
    device.config.session = MagicMock()
    device.vapix.initialize = AsyncMock()

    class _CancelledEvent:
        async def wait(self) -> None:
            raise asyncio.CancelledError

    with (
        patch("axis.__main__.axis_device", new=AsyncMock(return_value=device)),
        patch("axis.__main__.asyncio.Event", return_value=_CancelledEvent()),
        patch("axis.__main__.close_session", new=AsyncMock()) as close,
    ):
        await main(
            "camera.local",
            80,
            "root",
            "secret",
            params=True,
            events=True,
            web_proto=WebProtocol.HTTP,
            stream_mode="event",
        )

    device.enable_events.assert_called_once()
    device.event.subscribe.assert_called_once()
    device.stream.start.assert_called_once()
    assert device.stream.stop.call_count == 2
    close.assert_awaited_once_with(device.config.session)


def test_module_entrypoint_parses_arguments_and_calls_main(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Module execution reaches the same canonical CLI as the installed executable."""
    monkeypatch.setattr(sys, "argv", ["axis", "--help"])
    entrypoint = Path(__file__).resolve().parents[1] / "axis" / "__main__.py"
    with patch("axis.cli.entrypoint.main") as run:
        runpy.run_path(str(entrypoint), run_name="__main__")
    run.assert_called_once()


def test_module_entrypoint_logs_keyboard_interrupt(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Legacy positional credentials are rejected rather than routed or logged."""
    monkeypatch.setattr(sys, "argv", ["axis", "camera.local", "root", "secret"])
    entrypoint = Path(__file__).resolve().parents[1] / "axis" / "__main__.py"
    with pytest.raises(SystemExit) as caught:
        runpy.run_path(str(entrypoint), run_name="__main__")
    assert caught.value.code == 2
    assert "secret" not in capsys.readouterr().err


def test_event_handler_logs_event(caplog: pytest.LogCaptureFixture) -> None:
    """Forward received events to the module logger."""
    event = MagicMock()
    with caplog.at_level(logging.INFO, logger="axis.__main__"):
        event_handler(event)

    assert caplog.records[-1].message == str(event)
