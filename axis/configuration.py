"""Python library to enable Axis devices to integrate with Home Assistant."""

from dataclasses import KW_ONLY, dataclass

from httpx import AsyncClient


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

    @property
    def url(self) -> str:
        """Represent device base url."""
        return f"{self.web_proto}://{self.host}:{self.port}"
