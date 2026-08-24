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


async def test_aiohttp_client_session_request(
    aiohttp_mock_server: Any, session
) -> None:
    """Verify requests work with aiohttp ClientSession."""

    async def handle(_request: web.Request) -> web.Response:
        return web.Response(body=b"ok")

    axis_device = AxisDevice(
        Configuration(
            session,
            HOST,
            username=USER,
            password=PASS,
            port=80,
        )
    )

    await aiohttp_mock_server(
        "/axis-cgi/basicdeviceinfo.cgi",
        handler=handle,
        method="GET",
        device=axis_device,
        capture_requests=False,
    )

    result = await axis_device.vapix.request("get", "/axis-cgi/basicdeviceinfo.cgi")

    assert result == b"ok"


async def test_aiohttp_client_session_auto_auth_fallback_to_basic(
    aiohttp_mock_server: Any,
    session,
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

    axis_device = AxisDevice(
        Configuration(
            session,
            HOST,
            username=USER,
            password=PASS,
            port=80,
        )
    )

    await aiohttp_mock_server(
        "/axis-cgi/basicdeviceinfo.cgi",
        handler=handle,
        method="GET",
        device=axis_device,
        capture_requests=False,
    )

    result = await axis_device.vapix.request("get", "/axis-cgi/basicdeviceinfo.cgi")

    assert result == b"ok"
    assert calls == 2
    assert isinstance(axis_device.vapix.auth, aiohttp.BasicAuth)
    assert axis_device.vapix._aiohttp_digest_middleware is None


@pytest.mark.skipif(
    not hasattr(aiohttp, "DigestAuthMiddleware"),
    reason="DigestAuthMiddleware is unavailable in installed aiohttp",
)
async def test_aiohttp_client_session_auto_initializes_digest_middleware(
    aiohttp_mock_server: Any,
    session,
) -> None:
    """Verify AUTO mode sets up digest middleware for aiohttp sessions."""

    async def handle(_request: web.Request) -> web.Response:
        return web.Response(body=b"ok")

    axis_device = AxisDevice(
        Configuration(
            session,
            HOST,
            username=USER,
            password=PASS,
            port=80,
            auth_scheme=AuthScheme.AUTO,
        )
    )

    await aiohttp_mock_server(
        "/axis-cgi/basicdeviceinfo.cgi",
        handler=handle,
        method="GET",
        device=axis_device,
        capture_requests=False,
    )

    assert axis_device.vapix.auth is None
    assert axis_device.vapix._aiohttp_digest_middleware is not None


@pytest.mark.skipif(
    not hasattr(aiohttp, "DigestAuthMiddleware"),
    reason="DigestAuthMiddleware is unavailable in installed aiohttp",
)
async def test_aiohttp_client_session_digest_initializes_digest_middleware(
    aiohttp_mock_server: Any,
    session,
) -> None:
    """Verify DIGEST mode sets up digest middleware for aiohttp sessions."""

    async def handle(_request: web.Request) -> web.Response:
        return web.Response(body=b"ok")

    axis_device = AxisDevice(
        Configuration(
            session,
            HOST,
            username=USER,
            password=PASS,
            port=80,
            auth_scheme=AuthScheme.DIGEST,
        )
    )

    await aiohttp_mock_server(
        "/axis-cgi/basicdeviceinfo.cgi",
        handler=handle,
        method="GET",
        device=axis_device,
        capture_requests=False,
    )

    assert axis_device.vapix.auth is None
    assert axis_device.vapix._aiohttp_digest_middleware is not None


async def test_aiohttp_digest_middleware_signs_encoded_query(
    aiohttp_mock_server: Any,
    session,
) -> None:
    """Verify aiohttp digest middleware signs the encoded request target."""
    calls = 0

    async def handle(request: web.Request) -> web.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return web.Response(
                status=401,
                headers={
                    "WWW-Authenticate": (
                        'Digest realm="AXIS", nonce="abc123", algorithm=MD5, qop="auth"'
                    )
                },
            )

        assert request.raw_path == "/axis-cgi/io/port.cgi?action=9:%5C"
        assert request.headers["Authorization"].startswith("Digest ")
        return web.Response(body=b"ok")

    axis_device = AxisDevice(
        Configuration(
            session,
            HOST,
            username=USER,
            password=PASS,
            auth_scheme=AuthScheme.DIGEST,
        )
    )

    await aiohttp_mock_server(
        "/axis-cgi/io/port.cgi",
        handler=handle,
        method="GET",
        device=axis_device,
        capture_requests=False,
    )

    result = await axis_device.vapix.request(
        "get",
        "/axis-cgi/io/port.cgi",
        params={"action": "9:\\"},
    )

    assert result == b"ok"
    assert calls == 2
