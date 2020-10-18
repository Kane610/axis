"""Python library to enable Axis devices to integrate with Home Assistant."""

import attr
import httpx


@attr.s
class Configuration -> None:
    """Device configuration."""

    host: str = attr.ib()
    username: str = attr.ib(kw_only=True)
    password: str = attr.ib(kw_only=True)
    port: int = attr.ib(default=80, kw_only=True)
    web_proto: str = attr.ib(default="http", kw_only=True)
    verify_ssl: bool = attr.ib(default=False, kw_only=True)

    session: httpx.Client = attr.ib()

    @session.default
    def prepare_session(self) -> httpx.Client:
        session = httpx.Client()
        session.auth = httpx.DigestAuth(self.username, self.password)
        session.verify = self.verify_ssl
        return session

    @property
    def url(self) -> str:
        """Represent device base url."""
        return f"{self.web_proto}://{self.host}:{self.port}"
