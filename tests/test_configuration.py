"""Test Axis API Discovery API.

pytest --cov-report term-missing --cov=axis.configuration tests/test_configuration.py
"""

from typing import TYPE_CHECKING, cast

import pytest

from axis.models.configuration import AuthScheme, Configuration, WebProtocol

if TYPE_CHECKING:
    from aiohttp import ClientSession


async def test_configuration(session: ClientSession) -> None:
    """Test Configuration works."""
    config = Configuration(
        session,
        "192.168.0.1",
        username="root",
        password="pass",
        port=443,
        web_proto="https",
        verify_ssl=True,
    )

    assert config.host == "192.168.0.1"
    assert config.username == "root"
    assert config.password == "pass"
    assert config.port == 443
    assert config.web_proto == WebProtocol.HTTPS
    assert config.verify_ssl is True
    assert config.url == "https://192.168.0.1:443"
    assert config.is_companion is False
    assert config.auth_scheme == AuthScheme.AUTO
    assert config.websocket_enabled is False
    assert config.websocket_force is False


async def test_minimal_configuration(session: ClientSession) -> None:
    """Test Configuration works."""
    config = Configuration(
        session,
        "192.168.1.1",
        username="bill",
        password="cipher",
    )

    assert config.host == "192.168.1.1"
    assert config.username == "bill"
    assert config.password == "cipher"
    assert config.port == 80
    assert config.web_proto == WebProtocol.HTTP
    assert config.verify_ssl is False
    assert config.url == "http://192.168.1.1:80"
    assert config.is_companion is False
    assert config.auth_scheme == AuthScheme.AUTO
    assert config.websocket_enabled is False
    assert config.websocket_force is False


async def test_configuration_websocket_can_be_enabled(session: ClientSession) -> None:
    """Test websocket transport can be explicitly enabled."""
    config = Configuration(
        session,
        "192.168.1.10",
        username="root",
        password="pass",
        websocket_enabled=True,
    )

    assert config.websocket_enabled is True
    assert config.websocket_force is False


def test_unsupported_auth_scheme_defaults_to_auto() -> None:
    """Test unsupported auth scheme maps to AUTO."""
    assert AuthScheme("unsupported") == AuthScheme.AUTO


async def test_configuration_auth_scheme_is_normalized_to_enum(
    session: ClientSession,
) -> None:
    """Test auth scheme input is normalized to enum value."""
    config = Configuration(
        session,
        "192.168.1.2",
        username="root",
        password="pass",
        auth_scheme=cast("AuthScheme", "basic"),
    )

    assert config.auth_scheme is AuthScheme.BASIC


def test_unsupported_web_protocol_defaults_to_http() -> None:
    """Test unsupported web protocol maps to HTTP."""
    assert WebProtocol("unsupported") == WebProtocol.HTTP


async def test_configuration_web_protocol_is_normalized_to_enum(
    session: ClientSession,
) -> None:
    """Test web protocol input is normalized to enum value."""
    config = Configuration(
        session,
        "192.168.1.3",
        username="root",
        password="pass",
        web_proto=cast("WebProtocol", "https"),
    )

    assert config.web_proto is WebProtocol.HTTPS


async def test_configuration_default_https_port_is_443(session: ClientSession) -> None:
    """Test default HTTPS configuration uses port 443."""
    config = Configuration(
        session,
        "192.168.1.4",
        username="root",
        password="pass",
        web_proto=WebProtocol.HTTPS,
    )

    assert config.port == 443
    assert config.url == "https://192.168.1.4:443"


async def test_configuration_zero_port_uses_http_default(
    session: ClientSession,
) -> None:
    """Test port 0 uses HTTP default port."""
    config = Configuration(
        session,
        "192.168.1.5",
        username="root",
        password="pass",
        port=0,
        web_proto=WebProtocol.HTTP,
    )

    assert config.port == 80
    assert config.url == "http://192.168.1.5:80"


@pytest.mark.parametrize(
    "host",
    [
        "https://camera.local",
        "camera.local/path",
        "camera.local?foo=bar",
        "camera.local#anchor",
        "",
        " camera.local ",
    ],
)
async def test_configuration_rejects_invalid_host_values(
    session: ClientSession, host: str
) -> None:
    """Test host must be a plain hostname or IP address."""
    with pytest.raises(ValueError, match="Host must"):
        Configuration(
            session,
            host,
            username="root",
            password="pass",
        )
