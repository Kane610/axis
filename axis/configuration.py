"""Python library to enable Axis devices to integrate with Home Assistant."""

import attr

from httpx import AsyncClient


@attr.s
class Configuration:
    """Device configuration."""

    session: AsyncClient = attr.ib()
    host: str = attr.ib()
    username: str = attr.ib(kw_only=True)
    password: str = attr.ib(kw_only=True)
    port: int = attr.ib(default=80, kw_only=True)
    web_proto: str = attr.ib(default="http", kw_only=True)
    verify_ssl: bool = attr.ib(default=False, kw_only=True)

    @property
    def url(self) -> str:
        """Represent device base url."""
        return f"{self.web_proto}://{self.host}:{self.port}"
