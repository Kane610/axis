"""Read and update saved devices in a TOML file without losing unrelated settings.

Writes lock the file and replace it only after the new contents are complete.
The existing connection format is preserved, including unrecognized fields.
"""

from contextlib import contextmanager
from dataclasses import asdict, fields
import os
from pathlib import Path
import tomllib
from typing import TYPE_CHECKING, Any
from uuid import uuid4

import tomli_w

from axis.application.errors import StorageError, _fail
from axis.application.records import ConnectionSettings, DeviceRecord

__all__ = [
    "ConnectionSettings",
    "DeviceRecord",
    "DeviceRegistry",
    "StorageError",
    "default_config_path",
]

if TYPE_CHECKING:
    from collections.abc import Generator
    from types import ModuleType

if os.name == "posix":
    import fcntl as _fcntl

    fcntl: ModuleType | None = _fcntl
else:
    fcntl = None


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
    msg = "Device not found; use an exact registered serial or alias."
    raise StorageError(msg) from None


class DeviceRegistry:
    """Store devices locally and prevent simultaneous writers from corrupting the file.

    Mutations are unsupported on non-POSIX platforms rather than proceeding
    without locking. Readers do not create files and see atomic snapshots.
    """

    def __init__(self, path: Path) -> None:
        """Choose the configuration file without creating or reading it."""
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
        """Read saved devices, or return an empty dictionary if the file does not exist."""
        return _records(self._read())

    def resolve(self, identifier: str) -> DeviceRecord:
        """Resolve only an exact serial or alias, never a host address."""
        return _resolve(self.load(), identifier)

    @contextmanager
    def _locked(self) -> Generator[None]:
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

    def upsert(self, record: DeviceRecord, *, preserve_alias: bool = False) -> None:
        """Save a complete device record while keeping unrecognized configuration fields.

        Full-record updates are last-writer-wins, including stale records.
        Use update_credentials for a credentials-only read-modify-write.
        With preserve_alias, keep the latest stored alias (empty for new
        records) and reflect it on record after the write succeeds.
        """
        record.__post_init__()
        with self._locked():
            data = self._read()
            _records(data)
            devices = data.setdefault("devices", {})
            entry = devices.setdefault(record.serial, {})
            alias = entry.get("alias", "") if preserve_alias else record.alias
            entry.update(alias=alias, model=record.model)
            entry.setdefault("config", {}).update(asdict(record.config))
            _records(data)
            self._write(data)
            record.alias = alias

    def update_credentials(
        self, identifier: str, username: str, password: str
    ) -> DeviceRecord:
        """Replace login credentials without overwriting other saved device changes."""
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

    def update_alias(self, identifier: str, alias: str) -> DeviceRecord:
        """Set or clear the friendly name without overwriting other saved device changes."""
        with self._locked():
            data = self._read()
            record = _resolve(_records(data), identifier)
            record.alias = alias
            record.__post_init__()
            data["devices"][record.serial]["alias"] = alias
            _records(data)
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
