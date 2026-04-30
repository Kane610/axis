"""Test HTTP auth scheme behavior."""

import aiohttp
from aiohttp import web
import pytest

from axis.device import AxisDevice
from axis.errors import Unauthorized
from axis.models.configuration import AuthScheme, Configuration

from .conftest import HOST, PASS, USER


async def test_auth_scheme_auto_fallback_to_basic(aiohttp_mock_server):
    """Verify AUTO starts with digest and retries with basic auth once."""
    auth_headers: list[str] = []

    async def handle_basic_device_info(request: web.Request) -> web.Response:
        auth_headers.append(request.headers.get("Authorization", ""))
        if len(auth_headers) == 1:
            return web.Response(
                status=401,
                headers={"WWW-Authenticate": 'Basic realm="AXIS"'},
            )
        return web.Response(status=200, body=b"ok")

    session = aiohttp.ClientSession()
    axis_device = AxisDevice(
        Configuration(
            session,
            HOST,
            port=80,
            username=USER,
            password=PASS,
        )
    )

    await aiohttp_mock_server(
        "/axis-cgi/basicdeviceinfo.cgi",
        handler=handle_basic_device_info,
        method="GET",
        device=axis_device,
        capture_requests=False,
    )

    assert axis_device.vapix.auth is None

    try:
        result = await axis_device.vapix.request("get", "/axis-cgi/basicdeviceinfo.cgi")
    finally:
        await session.close()

    assert result == b"ok"
    assert isinstance(axis_device.vapix.auth, aiohttp.BasicAuth)
    assert len(auth_headers) == 2
    assert auth_headers[-1].lower().startswith("basic ")


async def test_auth_scheme_digest_does_not_fallback(aiohttp_mock_server):
    """Verify DIGEST does not switch auth method when basic is offered."""
    calls = 0

    async def handle_basic_device_info(_: web.Request) -> web.Response:
        nonlocal calls
        calls += 1
        return web.Response(
            status=401,
            headers={"WWW-Authenticate": 'Basic realm="AXIS"'},
        )

    session = aiohttp.ClientSession()
    axis_device = AxisDevice(
        Configuration(
            session,
            HOST,
            port=80,
            username=USER,
            password=PASS,
            auth_scheme=AuthScheme.DIGEST,
        )
    )

    await aiohttp_mock_server(
        "/axis-cgi/basicdeviceinfo.cgi",
        handler=handle_basic_device_info,
        method="GET",
        device=axis_device,
        capture_requests=False,
    )

    try:
        with pytest.raises(Unauthorized):
            await axis_device.vapix.request("get", "/axis-cgi/basicdeviceinfo.cgi")
    finally:
        await session.close()

    assert axis_device.vapix.auth is None
    assert calls == 1


async def test_auth_scheme_basic_initializes_basic_auth() -> None:
    """Verify BASIC starts with basic auth immediately."""
    session = aiohttp.ClientSession()
    axis_device = AxisDevice(
        Configuration(
            session,
            HOST,
            username=USER,
            password=PASS,
            auth_scheme=AuthScheme.BASIC,
        )
    )
    try:
        assert isinstance(axis_device.vapix.auth, aiohttp.BasicAuth)
    finally:
        await session.close()


async def test_auto_should_retry_guards() -> None:
    """Verify retry guard conditions short-circuit appropriately."""
    headers = {"WWW-Authenticate": 'Basic realm="AXIS"'}

    session = aiohttp.ClientSession()
    axis_device = AxisDevice(
        Configuration(
            session,
            HOST,
            username=USER,
            password=PASS,
            auth_scheme=AuthScheme.AUTO,
        )
    )
    try:
        # Retry disabled should always return False.
        assert not axis_device.vapix._should_retry_with_basic(headers, False)

        # On the aiohttp client path, retry guard does not inspect auth type.
        axis_device.vapix.auth = aiohttp.BasicAuth(USER, PASS)
        assert axis_device.vapix._should_retry_with_basic(headers, True)
    finally:
        await session.close()
