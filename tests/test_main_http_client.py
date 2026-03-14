"""Test CLI HTTP client backend selection."""

import aiohttp
from httpx import AsyncClient
import pytest

from axis.__main__ import close_session, create_session


async def test_create_session_httpx() -> None:
    """Verify httpx backend creates an AsyncClient."""
    session = create_session("httpx")

    try:
        assert isinstance(session, AsyncClient)
    finally:
        await close_session(session)


@pytest.mark.skipif(aiohttp is None, reason="aiohttp is not installed")
async def test_create_session_aiohttp() -> None:
    """Verify aiohttp backend creates a ClientSession."""
    session = create_session("aiohttp")

    try:
        assert isinstance(session, aiohttp.ClientSession)
    finally:
        await close_session(session)


async def test_close_session_httpx() -> None:
    """Verify close_session closes httpx sessions."""
    session = AsyncClient(verify=False)
    await close_session(session)
    assert session.is_closed


@pytest.mark.skipif(aiohttp is None, reason="aiohttp is not installed")
async def test_close_session_aiohttp() -> None:
    """Verify close_session closes aiohttp sessions."""
    session = aiohttp.ClientSession()
    await close_session(session)
    assert session.closed
