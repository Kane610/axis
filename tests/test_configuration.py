"""Test configuration defaults and normalization for device connections.

pytest --cov-report term-missing --cov=axis.configuration tests/test_configuration.py
"""

from typing import TYPE_CHECKING, cast

import pytest

from axis.models.configuration import AuthScheme, Configuration, WebProtocol

if TYPE_CHECKING:
    from aiohttp import ClientSession


async def test_configuration(session: ClientSession) -> None:
    """Keep explicitly supplied HTTPS connection and transport settings."""
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
    """Fill in HTTP defaults when only host and credentials are supplied."""
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
    """Allow WebSocket transport without forcing it."""
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
    """Map an unknown authentication scheme to automatic selection."""
    assert AuthScheme("unsupported") == AuthScheme.AUTO


async def test_configuration_auth_scheme_is_normalized_to_enum(
    session: ClientSession,
) -> None:
    """Convert a string authentication scheme to its enum member."""
    config = Configuration(
        session,
        "192.168.1.2",
        username="root",
        password="pass",
        auth_scheme=cast("AuthScheme", "basic"),
    )

    assert config.auth_scheme is AuthScheme.BASIC


def test_unsupported_web_protocol_defaults_to_http() -> None:
    """Map an unknown web protocol to HTTP."""
    assert WebProtocol("unsupported") == WebProtocol.HTTP


async def test_configuration_web_protocol_is_normalized_to_enum(
    session: ClientSession,
) -> None:
    """Convert a string web protocol to its enum member."""
    config = Configuration(
        session,
        "192.168.1.3",
        username="root",
        password="pass",
        web_proto=cast("WebProtocol", "https"),
    )

    assert config.web_proto is WebProtocol.HTTPS


async def test_configuration_default_https_port_is_443(session: ClientSession) -> None:
    """Choose port 443 when HTTPS is selected without an explicit port."""
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
    """Replace port zero with the default HTTP port."""
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
        "camera local",
        "",
        " camera.local ",
    ],
)
async def test_configuration_rejects_invalid_host_values(
    session: ClientSession, host: str
) -> None:
    """Reject hosts containing a scheme, path, query, whitespace, or no value."""
    with pytest.raises(ValueError, match="Host must"):
        Configuration(
            session,
            host,
            username="root",
            password="pass",
        )
