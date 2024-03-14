"""Python library to enable Axis devices to integrate with Home Assistant."""

from dataclasses import KW_ONLY, dataclass
import enum

from httpx import AsyncClient


class WebProtocol(enum.StrEnum):
    """Web protocol for Axis configuration."""

    HTTP = "http"
    HTTPS = "https"


@dataclass
class Configuration:
    """Device configuration."""

    session: AsyncClient
    host: str
    _: KW_ONLY
    username: str
    password: str
    port: int = 80
    web_proto: str = WebProtocol.HTTP
    verify_ssl: bool = False

    @property
    def url(self) -> str:
        """Represent device base url."""
        return f"{self.web_proto}://{self.host}:{self.port}"
