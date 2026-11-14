"""Connection settings for an Axis device's HTTP and event-stream APIs."""

from dataclasses import KW_ONLY, dataclass
import enum
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp import ClientSession


LOGGER = logging.getLogger(__name__)


class AuthScheme(enum.StrEnum):
    """Supported HTTP authentication schemes."""

    AUTO = "auto"
    BASIC = "basic"
    DIGEST = "digest"

    @classmethod
    def _missing_(cls, value: object) -> AuthScheme:
        """Use automatic authentication when the configured scheme is unknown."""
        LOGGER.debug("Unsupported auth scheme '%s'", value)
        return AuthScheme.AUTO


class WebProtocol(enum.StrEnum):
    """Supported web protocols."""

    HTTP = "http"
    HTTPS = "https"

    @classmethod
    def _missing_(cls, value: object) -> WebProtocol:
        """Use HTTP when the configured protocol is not recognized."""
        LOGGER.debug("Unsupported web protocol '%s'", value)
        return WebProtocol.HTTP


@dataclass
class Configuration:
    """HTTP session, address, credentials, and transport options for one device.

    A port value of 0 means use the default port for the configured protocol.
    """

    session: ClientSession
    host: str
    _: KW_ONLY
    username: str
    password: str
    port: int = 0
    web_proto: WebProtocol = WebProtocol.HTTP
    verify_ssl: bool = False
    is_companion: bool = False
    auth_scheme: AuthScheme = AuthScheme.AUTO
    websocket_enabled: bool = False
    websocket_force: bool = False

    def __post_init__(self) -> None:
        """Coerce transport settings and choose the protocol's default port."""
        self.web_proto = WebProtocol(self.web_proto)
        self._validate_host()
        if self.port == 0:
            self.port = 443 if self.web_proto == WebProtocol.HTTPS else 80
        self.auth_scheme = AuthScheme(self.auth_scheme)

    def _validate_host(self) -> None:
        """Reject hosts containing URL components or invalid whitespace."""
        if not self.host or self.host.strip() != self.host:
            msg = "Host must be a non-empty hostname or IP address"
            raise ValueError(msg)

        if " " in self.host:
            msg = "Host must not contain spaces"
            raise ValueError(msg)

        if "://" in self.host or any(char in self.host for char in ("/", "?", "#")):
            msg = (
                "Host must not include scheme, path, query, or fragment; "
                "use host, web_proto, and port separately"
            )
            raise ValueError(msg)

    @property
    def url(self) -> str:
        """Return the device's base URL, including its protocol and port."""
        return f"{self.web_proto}://{self.host}:{self.port}"
