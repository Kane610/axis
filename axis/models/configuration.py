"""Python library to enable Axis devices to integrate with Home Assistant."""

from dataclasses import KW_ONLY, dataclass
import enum
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import AsyncClient


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


@dataclass
class Configuration:
    """Device configuration."""

    session: AsyncClient
    host: str
    _: KW_ONLY
    username: str
    password: str
    port: int = 80
    web_proto: str = "http"
    verify_ssl: bool = False
    is_companion: bool = False
    auth_scheme: AuthScheme = AuthScheme.AUTO

    def __post_init__(self) -> None:
        """Normalize auth scheme value to enum."""
        self.auth_scheme = AuthScheme(self.auth_scheme)

    @property
    def url(self) -> str:
        """Represent device base url."""
        return f"{self.web_proto}://{self.host}:{self.port}"
