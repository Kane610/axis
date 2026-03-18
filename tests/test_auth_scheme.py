"""Test HTTP auth scheme behavior."""

from typing import Any

import aiohttp
from aiohttp import web
import pytest

from axis.device import AxisDevice
from axis.errors import Unauthorized
from axis.models.configuration import AuthScheme, Configuration

HOST = "127.0.0.1"
USER = "root"
PASS = "pass"


async def test_auth_scheme_auto_fallback_to_basic(aiohttp_server: Any):
    """Verify AUTO retries with basic auth once when server asks for basic auth."""
    calls = 0
    last_authorization = ""

    async def handle(request: web.Request) -> web.Response:
        nonlocal calls
        nonlocal last_authorization

        calls += 1
        last_authorization = request.headers.get("Authorization", "")

        if calls == 1:
            return web.Response(
                status=401,
                headers={"WWW-Authenticate": 'Basic realm="AXIS"'},
            )

        if last_authorization.lower().startswith("basic "):
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
            auth_scheme=AuthScheme.AUTO,
        )
    )

    try:
        assert axis_device.vapix.auth is None

        result = await axis_device.vapix.request("get", "/axis-cgi/basicdeviceinfo.cgi")

        assert result == b"ok"
        assert isinstance(axis_device.vapix.auth, aiohttp.BasicAuth)
        assert calls == 2
        assert last_authorization.lower().startswith("basic ")
    finally:
        await session.close()


async def test_auth_scheme_digest_does_not_fallback(aiohttp_server: Any):
    """Verify DIGEST does not switch auth method when basic is offered."""

    async def handle(_request: web.Request) -> web.Response:
        return web.Response(
            status=401,
            headers={"WWW-Authenticate": 'Basic realm="AXIS"'},
        )

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
        with pytest.raises(Unauthorized):
            await axis_device.vapix.request("get", "/axis-cgi/basicdeviceinfo.cgi")
    finally:
        await session.close()

    assert axis_device.vapix.auth is None


def test_auth_scheme_basic_initializes_basic_auth(axis_device: AxisDevice) -> None:
    """Verify BASIC starts with basic auth immediately."""
    axis_device.config.auth_scheme = AuthScheme.BASIC
    axis_device.vapix = axis_device.vapix.__class__(axis_device)

    assert isinstance(axis_device.vapix.auth, aiohttp.BasicAuth)


def test_auto_should_retry_guards(axis_device: AxisDevice) -> None:
    """Verify retry guard conditions short-circuit appropriately."""
    headers = {"WWW-Authenticate": 'Basic realm="AXIS"'}

    # Retry disabled should always return False.
    assert not axis_device.vapix._should_retry_with_basic(headers, False)

    # BASIC mode should never trigger AUTO retry.
    axis_device.config.auth_scheme = AuthScheme.BASIC
    assert not axis_device.vapix._should_retry_with_basic(headers, True)
