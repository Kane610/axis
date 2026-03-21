"""Python library to enable Axis devices to integrate with Home Assistant."""

from dataclasses import KW_ONLY, dataclass
import enum
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp import ClientSession
    from httpx import AsyncClient

    type HTTPSession = AsyncClient | ClientSession


LOGGER = logging.getLogger(__name__)


class AuthScheme(enum.StrEnum):
    """Supported HTTP authentication schemes."""

    AUTO = "auto"
    BASIC = "basic"
    DIGEST = "digest"

    @classmethod
    def _missing_(cls, value: object) -> AuthScheme:
        """Set default enum member if an unknown value is provided."""
        LOGGER.debug("Unsupported auth scheme '%s'", value)
        return AuthScheme.AUTO


class WebProtocol(enum.StrEnum):
    """Supported web protocols."""

    HTTP = "http"
    HTTPS = "https"

    @classmethod
    def _missing_(cls, value: object) -> WebProtocol:
        """Set default enum member if an unknown value is provided."""
        LOGGER.debug("Unsupported web protocol '%s'", value)
        return WebProtocol.HTTP


@dataclass
class Configuration:
    """Device configuration.

    A port value of 0 means use the default port for the configured protocol.
    """

    session: HTTPSession
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

    def __post_init__(self) -> None:
        """Normalize auth and protocol values to enums and resolve default port."""
        self.web_proto = WebProtocol(self.web_proto)
        self._validate_host()
        if self.port == 0:
            self.port = 443 if self.web_proto == WebProtocol.HTTPS else 80
        self.auth_scheme = AuthScheme(self.auth_scheme)

    def _validate_host(self) -> None:
        """Validate that host is a plain hostname or IP address."""
        if not self.host or self.host.strip() != self.host:
            msg = "Host must be a non-empty hostname or IP address"
            raise ValueError(msg)

        if "://" in self.host or any(char in self.host for char in ("/", "?", "#")):
            msg = (
                "Host must not include scheme, path, query, or fragment; "
                "use host, web_proto, and port separately"
            )
            raise ValueError(msg)

    @property
    def url(self) -> str:
        """Represent device base url."""
        return f"{self.web_proto}://{self.host}:{self.port}"
