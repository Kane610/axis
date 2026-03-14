"""Test HTTP auth scheme behavior."""

import httpx
import pytest

from axis.device import AxisDevice
from axis.errors import Unauthorized
from axis.models.configuration import AuthScheme, Configuration

HOST = "127.0.0.1"
USER = "root"
PASS = "pass"


async def test_auth_scheme_auto_fallback_to_basic(respx_mock, axis_device: AxisDevice):
    """Verify AUTO starts with digest and retries with basic auth once."""
    route = respx_mock.get("/axis-cgi/basicdeviceinfo.cgi").mock(
        side_effect=[
            httpx.Response(
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="AXIS"'},
            ),
            httpx.Response(status_code=200, content=b"ok"),
        ]
    )

    assert isinstance(axis_device.vapix.auth, httpx.DigestAuth)

    result = await axis_device.vapix.request("get", "/axis-cgi/basicdeviceinfo.cgi")

    assert result == b"ok"
    assert isinstance(axis_device.vapix.auth, httpx.BasicAuth)
    assert len(route.calls) == 2
    assert (
        route.calls.last.request.headers["authorization"].lower().startswith("basic ")
    )


async def test_auth_scheme_digest_does_not_fallback(respx_mock):
    """Verify DIGEST does not switch auth method when basic is offered."""
    respx_mock(base_url=f"http://{HOST}:80")

    session = httpx.AsyncClient(verify=False)
    axis_device = AxisDevice(
        Configuration(
            session,
            HOST,
            username=USER,
            password=PASS,
            auth_scheme=AuthScheme.DIGEST,
        )
    )

    route = respx_mock.get("/axis-cgi/basicdeviceinfo.cgi").respond(
        status_code=401,
        headers={"WWW-Authenticate": 'Basic realm="AXIS"'},
    )

    try:
        with pytest.raises(Unauthorized):
            await axis_device.vapix.request("get", "/axis-cgi/basicdeviceinfo.cgi")
    finally:
        await session.aclose()

    assert isinstance(axis_device.vapix.auth, httpx.DigestAuth)
    assert len(route.calls) == 1


def test_auth_scheme_basic_initializes_basic_auth(axis_device: AxisDevice) -> None:
    """Verify BASIC starts with basic auth immediately."""
    axis_device.config.auth_scheme = AuthScheme.BASIC
    axis_device.vapix = axis_device.vapix.__class__(axis_device)

    assert isinstance(axis_device.vapix.auth, httpx.BasicAuth)


def test_auto_should_retry_guards(axis_device: AxisDevice) -> None:
    """Verify retry guard conditions short-circuit appropriately."""
    headers = httpx.Headers({"WWW-Authenticate": 'Basic realm="AXIS"'})

    # Retry disabled should always return False.
    assert not axis_device.vapix._should_retry_with_basic(headers, False)

    # AUTO mode with basic auth should not retry.
    axis_device.vapix.auth = httpx.BasicAuth(USER, PASS)
    assert not axis_device.vapix._should_retry_with_basic(headers, True)
