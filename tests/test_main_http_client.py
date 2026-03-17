"""Test CLI HTTP client backend selection."""

import aiohttp

from axis.__main__ import close_session, create_session


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
