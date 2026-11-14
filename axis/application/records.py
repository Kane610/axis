"""Session-free application records, separate from VAPIX runtime configuration."""

from dataclasses import dataclass, field
from unicodedata import category

from .errors import _fail


def _has_unsafe_characters(identifier: str) -> bool:
    return any(category(char) in ("Cc", "Cf", "Cs", "Zl", "Zp") for char in identifier)


@dataclass
class ConnectionSettings:
    """Stored connection settings; zero port selects the protocol default."""

    host: str
    username: str
    password: str = field(repr=False)
    port: int = 0
    web_proto: str = "http"
    verify_ssl: bool = False
    is_companion: bool = False
    auth_scheme: str = "auto"
    websocket_enabled: bool = False
    websocket_force: bool = False

    def __post_init__(self) -> None:
        """Reject malformed settings without echoing credential values."""
        if (
            not isinstance(self.host, str)
            or not self.host
            or any(char.isspace() for char in self.host)
            or any(char in self.host for char in ("://", "/", "?", "#"))
        ):
            _fail("Host must be a plain, non-empty hostname or IP address.")
        if not isinstance(self.username, str) or not self.username.strip():
            _fail("Username must be a non-empty string.")
        if not isinstance(self.password, str):
            _fail("Password must be a string.")
        if type(self.port) is not int or not 0 <= self.port <= 65535:
            _fail("Port must be an integer from 0 to 65535.")
        if self.web_proto not in ("http", "https"):
            _fail("Web protocol must be http or https.")
        if self.auth_scheme not in ("auto", "basic", "digest"):
            _fail("Authentication scheme must be auto, basic, or digest.")
        if any(
            type(getattr(self, name)) is not bool
            for name in (
                "verify_ssl",
                "is_companion",
                "websocket_enabled",
                "websocket_force",
            )
        ):
            _fail("Connection flags must be booleans.")


@dataclass
class DeviceRecord:
    """A canonical serial and optional exact-match alias for a stored device."""

    serial: str
    config: ConnectionSettings
    alias: str = ""
    model: str = ""

    def __post_init__(self) -> None:
        """Validate device identity and settings at the input boundary."""
        if (
            not isinstance(self.serial, str)
            or not self.serial.strip()
            or self.serial.strip() != self.serial
            or self.serial.casefold() == "unknown"
            or _has_unsafe_characters(self.serial)
        ):
            _fail(
                "Device serial must be non-empty, known, and free of control characters."
            )
        if (
            not isinstance(self.alias, str)
            or self.alias.strip() != self.alias
            or _has_unsafe_characters(self.alias)
        ):
            _fail(
                "Device alias must be a string without control characters or surrounding whitespace."
            )
        if not isinstance(self.model, str):
            _fail("Device model must be a string.")
        if not isinstance(self.config, ConnectionSettings):
            _fail("Device config must be ConnectionSettings.")
        self.config.__post_init__()
