"""Python library to enable Axis devices to integrate with Home Assistant."""

import attr
import requests
from requests.auth import HTTPDigestAuth


@attr.s
class Configuration:
    """Device configuration."""

    host: str = attr.ib()
    username: str = attr.ib(kw_only=True)
    password: str = attr.ib(kw_only=True)
    port: int = attr.ib(default=80, kw_only=True)
    web_proto: str = attr.ib(default="http", kw_only=True)
    verify_ssl: bool = attr.ib(default=False, kw_only=True)

    session: requests.Session = attr.ib()

    @session.default
    def prepare_session(self):
        session = requests.Session()
        session.auth = HTTPDigestAuth(self.username, self.password)
        session.verify = self.verify_ssl
        return session

    @property
    def url(self):
        """Represent device base url."""
        return f"{self.web_proto}://{self.host}:{self.port}"
