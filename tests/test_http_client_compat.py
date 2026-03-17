"""Test compatibility between supported HTTP clients."""

from typing import Any

import aiohttp
from aiohttp import web
import pytest

from axis.device import AxisDevice
from axis.models.configuration import AuthScheme, Configuration

HOST = "127.0.0.1"
USER = "root"
PASS = "pass"


async def test_aiohttp_client_session_request(aiohttp_server: Any) -> None:
    """Verify requests work with aiohttp ClientSession."""

    async def handle(_request: web.Request) -> web.Response:
        return web.Response(body=b"ok")

    app = web.Application()
    app.router.add_get("/axis-cgi/basicdeviceinfo.cgi", handle)
    server = await aiohttp_server(app)

    session = aiohttp.ClientSession()
    axis_device = AxisDevice(
        Configuration(
            session,
            HOST,
            username=USER,
            password=PASS,
            port=server.port,
        )
    )

    try:
        result = await axis_device.vapix.request("get", "/axis-cgi/basicdeviceinfo.cgi")
    finally:
        await session.close()

    assert result == b"ok"


async def test_aiohttp_client_session_auto_auth_fallback_to_basic(
    aiohttp_server: Any,
) -> None:
    """Verify AUTO retries once with basic auth when server requests it."""
    calls = 0

    async def handle(request: web.Request) -> web.Response:
        nonlocal calls
        calls += 1

        if calls == 1:
            return web.Response(
                status=401,
                headers={"WWW-Authenticate": 'Basic realm="AXIS"'},
            )

        auth = request.headers.get("Authorization", "").lower()
        if auth.startswith("basic "):
            return web.Response(body=b"ok")

        return web.Response(status=401)

    app = web.Application()
    app.router.add_get("/axis-cgi/basicdeviceinfo.cgi", handle)
    server = await aiohttp_server(app)

    session = aiohttp.ClientSession()
    axis_device = AxisDevice(
        Configuration(
            session,
            HOST,
            username=USER,
            password=PASS,
            port=server.port,
        )
    )

    try:
        result = await axis_device.vapix.request("get", "/axis-cgi/basicdeviceinfo.cgi")
    finally:
        await session.close()

    assert result == b"ok"
    assert calls == 2
    assert isinstance(axis_device.vapix.auth, aiohttp.BasicAuth)
    assert axis_device.vapix._aiohttp_middlewares() is None


@pytest.mark.skipif(
    not hasattr(aiohttp, "DigestAuthMiddleware"),
    reason="DigestAuthMiddleware is unavailable in installed aiohttp",
)
async def test_aiohttp_client_session_auto_initializes_digest_middleware(
    aiohttp_server: Any,
) -> None:
    """Verify AUTO mode sets up digest middleware for aiohttp sessions."""

    async def handle(_request: web.Request) -> web.Response:
        return web.Response(body=b"ok")

    app = web.Application()
    app.router.add_get("/axis-cgi/basicdeviceinfo.cgi", handle)
    server = await aiohttp_server(app)

    session = aiohttp.ClientSession()
    axis_device = AxisDevice(
        Configuration(
            session,
            HOST,
            username=USER,
            password=PASS,
            port=server.port,
            auth_scheme=AuthScheme.AUTO,
        )
    )

    try:
        assert axis_device.vapix.auth is None
        middlewares = axis_device.vapix._aiohttp_middlewares()
        assert middlewares is not None
        assert len(middlewares) == 1
    finally:
        await session.close()


@pytest.mark.skipif(
    not hasattr(aiohttp, "DigestAuthMiddleware"),
    reason="DigestAuthMiddleware is unavailable in installed aiohttp",
)
async def test_aiohttp_client_session_digest_initializes_digest_middleware(
    aiohttp_server: Any,
) -> None:
    """Verify DIGEST mode sets up digest middleware for aiohttp sessions."""

    async def handle(_request: web.Request) -> web.Response:
        return web.Response(body=b"ok")

    app = web.Application()
    app.router.add_get("/axis-cgi/basicdeviceinfo.cgi", handle)
    server = await aiohttp_server(app)

    session = aiohttp.ClientSession()
    axis_device = AxisDevice(
        Configuration(
            session,
            HOST,
            username=USER,
            password=PASS,
            port=server.port,
            auth_scheme=AuthScheme.DIGEST,
        )
    )

    try:
        assert axis_device.vapix.auth is None
        middlewares = axis_device.vapix._aiohttp_middlewares()
        assert middlewares is not None
        assert len(middlewares) == 1
    finally:
        await session.close()
