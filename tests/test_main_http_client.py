"""Test CLI HTTP client backend selection."""

import aiohttp
import pytest

from axis.__main__ import close_session, create_session, websocket_flags_from_mode


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
