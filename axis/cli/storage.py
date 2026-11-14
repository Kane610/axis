"""Typed CLI device registry preserving the legacy VAPIX connection TOML format."""

from contextlib import contextmanager
from dataclasses import asdict, dataclass, field, fields
import os
from pathlib import Path
import tomllib
from typing import TYPE_CHECKING, Any, Never
from unicodedata import category
from uuid import uuid4

import tomli_w

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import ModuleType

if os.name == "posix":
    import fcntl as _fcntl

    fcntl: ModuleType | None = _fcntl
else:
    fcntl = None


class StorageError(ValueError):
    """Safe, actionable registry validation or persistence failure."""


def _fail(message: str) -> Never:
    raise StorageError(message) from None


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


def default_config_path() -> Path:
    """Return ~/.axis/config.toml without creating directories or files."""
    return Path.home() / ".axis" / "config.toml"


def _records(data: dict[str, Any]) -> dict[str, DeviceRecord]:
    devices = data.get("devices", {})
    if not isinstance(devices, dict):
        _fail("The devices section must be a TOML table; repair the config file.")
    records: dict[str, DeviceRecord] = {}
    names = {item.name for item in fields(ConnectionSettings)}
    for serial, entry in devices.items():
        if not isinstance(entry, dict) or not isinstance(entry.get("config"), dict):
            _fail("Each device must have a config table; repair the config file.")
        config = entry["config"]
        if not {"host", "username", "password"} <= config.keys():
            _fail("Each config must contain host, username, and password.")
        records[serial] = DeviceRecord(
            serial=serial,
            config=ConnectionSettings(
                **{key: value for key, value in config.items() if key in names}
            ),
            alias=entry.get("alias", ""),
            model=entry.get("model", ""),
        )
    aliases: set[str] = set()
    for serial, record in records.items():
        if record.alias:
            if record.alias in aliases or (
                record.alias in records and record.alias != serial
            ):
                _fail("Device aliases must be unique and not match another serial.")
            aliases.add(record.alias)
    return records


def _resolve(records: dict[str, DeviceRecord], identifier: str) -> DeviceRecord:
    if not isinstance(identifier, str) or not identifier:
        _fail("Provide an exact registered serial or alias.")
    if identifier in records:
        return records[identifier]
    for record in records.values():
        if record.alias == identifier:
            return record
    _fail("Device not found; use an exact registered serial or alias.")


class DeviceRegistry:
    """Read and atomically mutate the registry under a POSIX advisory lock.

    Mutations are unsupported on non-POSIX platforms rather than proceeding
    without locking. Readers do not create files and see atomic snapshots.
    """

    def __init__(self, path: Path) -> None:
        """Select a config path without filesystem side effects."""
        self.path = path

    def _read(self) -> dict[str, Any]:
        try:
            with self.path.open("rb") as handle:
                return tomllib.load(handle)
        except FileNotFoundError:
            return {}
        except OSError, ValueError:
            _fail("Cannot read config; check permissions and repair invalid TOML.")

    def load(self) -> dict[str, DeviceRecord]:
        """Load validated records, returning an empty registry if absent."""
        return _records(self._read())

    def resolve(self, identifier: str) -> DeviceRecord:
        """Resolve only an exact serial or alias, never a host address."""
        return _resolve(self.load(), identifier)

    @contextmanager
    def _locked(self) -> Iterator[None]:
        if fcntl is None:
            _fail("Registry writes require POSIX advisory locking.")
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            descriptor = os.open(
                self.path.with_name(self.path.name + ".lock"),
                os.O_CREAT | os.O_RDWR,
                0o600,
            )
            with os.fdopen(descriptor, "rb") as handle:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        except OSError:
            _fail("Cannot update config; check directory permissions and retry.")

    def _write(self, data: dict[str, Any]) -> None:
        pending = self.path.with_name(f".{self.path.name}.{uuid4().hex}.pending")
        try:
            descriptor = os.open(pending, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            try:
                with os.fdopen(descriptor, "wb") as handle:
                    os.fchmod(handle.fileno(), 0o600)
                    tomli_w.dump(data, handle)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(pending, self.path)
            finally:
                pending.unlink(missing_ok=True)
        except OSError, ValueError, TypeError:
            _fail("Cannot save config; check directory permissions and retry.")

    def upsert(self, record: DeviceRecord) -> None:
        """Replace typed fields for a serial, preserving unrecognized TOML keys.

        Full-record updates are last-writer-wins, including stale records.
        Use update_credentials for a credentials-only read-modify-write.
        """
        record.__post_init__()
        with self._locked():
            data = self._read()
            _records(data)
            devices = data.setdefault("devices", {})
            entry = devices.setdefault(record.serial, {})
            entry.update(alias=record.alias, model=record.model)
            entry.setdefault("config", {}).update(asdict(record.config))
            _records(data)
            self._write(data)

    def update_credentials(
        self, identifier: str, username: str, password: str
    ) -> DeviceRecord:
        """Update only credentials on the latest record under the write lock."""
        with self._locked():
            data = self._read()
            record = _resolve(_records(data), identifier)
            record.config.username = username
            record.config.password = password
            record.config.__post_init__()
            data["devices"][record.serial]["config"].update(
                username=username, password=password
            )
            self._write(data)
            return record

    def remove(self, identifier: str) -> DeviceRecord:
        """Remove an exact serial or alias and return its validated record."""
        with self._locked():
            data = self._read()
            record = _resolve(_records(data), identifier)
            del data["devices"][record.serial]
            self._write(data)
            return record
