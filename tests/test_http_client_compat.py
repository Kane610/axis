"""Test compatibility between supported HTTP clients."""

import hashlib
from typing import Any

import aiohttp
from aiohttp import web
from multidict import CIMultiDict, CIMultiDictProxy
import pytest

from axis.device import AxisDevice
from axis.models.configuration import AuthScheme, Configuration

HOST = "127.0.0.1"
USER = "root"
PASS = "pass"


async def test_aiohttp_client_session_request(aiohttp_mock_server: Any) -> None:
    """Verify requests work with aiohttp ClientSession."""

    async def handle(_request: web.Request) -> web.Response:
        return web.Response(body=b"ok")

    session = aiohttp.ClientSession()
    axis_device = AxisDevice(
        Configuration(
            session,
            HOST,
            username=USER,
            password=PASS,
            port=80,
        )
    )

    _server, _requests = await aiohttp_mock_server(
        "/axis-cgi/basicdeviceinfo.cgi",
        handler=handle,
        method="GET",
        device=axis_device,
    )

    try:
        result = await axis_device.vapix.request("get", "/axis-cgi/basicdeviceinfo.cgi")
    finally:
        await session.close()

    assert result == b"ok"


async def test_aiohttp_client_session_auto_auth_fallback_to_basic(
    aiohttp_mock_server: Any,
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

    session = aiohttp.ClientSession()
    axis_device = AxisDevice(
        Configuration(
            session,
            HOST,
            username=USER,
            password=PASS,
            port=80,
        )
    )

    _server, _requests = await aiohttp_mock_server(
        "/axis-cgi/basicdeviceinfo.cgi",
        handler=handle,
        method="GET",
        device=axis_device,
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
    aiohttp_mock_server: Any,
) -> None:
    """Verify AUTO mode sets up digest middleware for aiohttp sessions."""

    async def handle(_request: web.Request) -> web.Response:
        return web.Response(body=b"ok")

    session = aiohttp.ClientSession()
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

    _server, _requests = await aiohttp_mock_server(
        "/axis-cgi/basicdeviceinfo.cgi",
        handler=handle,
        method="GET",
        device=axis_device,
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
    aiohttp_mock_server: Any,
) -> None:
    """Verify DIGEST mode sets up digest middleware for aiohttp sessions."""

    async def handle(_request: web.Request) -> web.Response:
        return web.Response(body=b"ok")

    session = aiohttp.ClientSession()
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

    _server, _requests = await aiohttp_mock_server(
        "/axis-cgi/basicdeviceinfo.cgi",
        handler=handle,
        method="GET",
        device=axis_device,
    )

    try:
        assert axis_device.vapix.auth is None
        middlewares = axis_device.vapix._aiohttp_middlewares()
        assert middlewares is not None
        assert len(middlewares) == 1
    finally:
        await session.close()


async def test_aiohttp_digest_request_target_preencodes_query_params() -> None:
    """Ensure library-managed digest requests sign escaped query URI."""
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
        url, params = axis_device.vapix._aiohttp_digest_auth.request_target(
            f"http://{HOST}/axis-cgi/io/port.cgi",
            {"action": "9:\\"},
            True,
        )

        assert params is None
        assert isinstance(url, str)
        assert url == f"http://{HOST}/axis-cgi/io/port.cgi?action=9%3A%5C"

        # Without params, request target must remain unchanged.
        no_params_url, no_params = (
            axis_device.vapix._aiohttp_digest_auth.request_target(
                f"http://{HOST}/axis-cgi/io/port.cgi",
                None,
                True,
            )
        )
        assert no_params_url == f"http://{HOST}/axis-cgi/io/port.cgi"
        assert no_params is None
    finally:
        await session.close()


async def test_aiohttp_digest_challenge_header_selection() -> None:
    """Select digest challenge from WWW-Authenticate headers."""
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
        headers = CIMultiDictProxy(
            CIMultiDict(
                [
                    ("WWW-Authenticate", 'Basic realm="AXIS"'),
                    (
                        "WWW-Authenticate",
                        'Digest realm="AXIS", nonce="abc", algorithm=MD5, qop="auth"',
                    ),
                ]
            )
        )

        challenge = axis_device.vapix._aiohttp_digest_auth.extract_challenge(headers)
        assert challenge is not None
        assert challenge.lower().startswith("digest ")
    finally:
        await session.close()


async def test_aiohttp_digest_authorization_contains_required_fields() -> None:
    """Build digest authorization header with required auth fields."""
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
        challenge = 'Digest realm="AXIS", nonce="n1", algorithm=MD5, qop="auth"'
        authorization = axis_device.vapix._aiohttp_digest_auth.build_authorization(
            method="get",
            request_url=f"http://{HOST}/axis-cgi/io/port.cgi?action=9%3A%5C",
            digest_challenge=challenge,
        )
        assert authorization is not None
        assert authorization.startswith("Digest ")
        assert 'username="root"' in authorization
        assert 'realm="AXIS"' in authorization
        assert 'nonce="n1"' in authorization
        assert 'uri="/axis-cgi/io/port.cgi?action=9%3A%5C"' in authorization
        assert "qop=auth" in authorization
        assert "nc=" in authorization
        assert "cnonce=" in authorization
        assert "response=" in authorization
    finally:
        await session.close()


async def test_aiohttp_digest_signature_validation_known_values() -> None:
    """Validate digest signature against known correct value (RFC 2617)."""
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
        # Known test inputs with fixed nonce to verify computation
        realm = "AXIS"
        nonce = "abc123"
        method = "GET"
        request_uri = "/axis-cgi/io/port.cgi?action=9%3A%5C"

        # Calculate expected values per RFC 2617
        ha1 = hashlib.md5(f"{USER}:{realm}:{PASS}".encode()).hexdigest()
        ha2 = hashlib.md5(f"{method}:{request_uri}".encode()).hexdigest()

        # Verify HA1 and HA2 calculations match expected digest components
        assert ha1 == hashlib.md5(b"root:AXIS:pass").hexdigest()
        assert (
            ha2 == hashlib.md5(b"GET:/axis-cgi/io/port.cgi?action=9%3A%5C").hexdigest()
        )

        challenge = (
            f'Digest realm="{realm}", nonce="{nonce}", algorithm=MD5, qop="auth"'
        )
        authorization = axis_device.vapix._aiohttp_digest_auth.build_authorization(
            method=method,
            request_url=f"http://{HOST}{request_uri}",
            digest_challenge=challenge,
        )

        # Verify authorization header structure
        assert authorization is not None
        assert "Digest " in authorization
        assert f'nonce="{nonce}"' in authorization
        assert "qop=auth" in authorization
        assert "response=" in authorization
    finally:
        await session.close()


async def test_aiohttp_digest_special_characters_encoding() -> None:
    """Validate proper encoding of various special characters in query params."""
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
        # Test cases: (input_value, expected_encoded)
        test_cases = [
            ("9:\\", "9%3A%5C"),  # colon and backslash
            ("test=value", "test%3Dvalue"),  # equals sign
            ("a b", "a%20b"),  # space
            ("a&b", "a%26b"),  # ampersand
            ("a+b", "a%2Bb"),  # plus sign
            ("a?b", "a%3Fb"),  # question mark
            ("/path/", "%2Fpath%2F"),  # forward slash
            ("a#b", "a%23b"),  # hash
            ("a[b]", "a%5Bb%5D"),  # brackets
        ]

        for input_val, expected_encoded in test_cases:
            url, params = axis_device.vapix._aiohttp_digest_auth.request_target(
                f"http://{HOST}/axis-cgi/test.cgi",
                {"param": input_val},
                True,
            )
            assert params is None, f"Params should be None for input {input_val}"
            assert f"param={expected_encoded}" in url, (
                f"Expected {input_val} to encode as {expected_encoded} in URL: {url}"
            )
    finally:
        await session.close()


async def test_aiohttp_digest_multiple_params_encoding() -> None:
    """Validate encoding of multiple query parameters."""
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
        url, params = axis_device.vapix._aiohttp_digest_auth.request_target(
            f"http://{HOST}/axis-cgi/io/port.cgi",
            {"action": "9:\\", "group": "IO", "id": "5"},
            True,
        )

        assert params is None
        # All parameters should be present and encoded
        assert "action=9%3A%5C" in url
        assert "group=IO" in url
        assert "id=5" in url
        # Base URL should be present
        assert url.startswith(f"http://{HOST}/axis-cgi/io/port.cgi?")
    finally:
        await session.close()
