"""Read and update saved devices in a TOML file without losing unrelated settings.

Writes lock the file and replace it only after the new contents are complete.
The existing connection format is preserved, including unrecognized fields.
"""

from contextlib import contextmanager
from dataclasses import asdict, fields
from datetime import datetime  # noqa: TC003 - public registry methods support runtime type introspection
from ipaddress import ip_address
import os
from pathlib import Path
import re
import tomllib
from typing import TYPE_CHECKING, Any
from uuid import uuid4

import tomli_w

from axis.application.errors import StorageError, _fail
from axis.application.records import (
    ConnectionSettings,
    DeviceRecord,
    DiscoverySnapshot,
    _validate_discovery_time,
)

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
        discovery = entry.get("discovery")
        if discovery is not None:
            if (
                not isinstance(discovery, dict)
                or not {"host", "last_seen"} <= discovery.keys()
            ):
                _fail("Each discovery table must contain host and last_seen.")
            discovery = DiscoverySnapshot(
                **{
                    item.name: discovery[item.name]
                    for item in fields(DiscoverySnapshot)
                    if item.name in discovery
                }
            )
        records[serial] = DeviceRecord(
            serial=serial,
            config=ConnectionSettings(
                **{key: value for key, value in config.items() if key in names}
            ),
            alias=entry.get("alias", ""),
            model=entry.get("model", ""),
            discovery=discovery,
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


def _mac_key(value: str) -> str:
    """Match complete MAC-like identifiers regardless of case or separators."""
    normalized = value.strip().lower().rstrip("*").replace(":", "").replace("-", "")
    return normalized if re.fullmatch(r"[0-9a-f]{12}", normalized) else ""


def _discovery_match(
    records: dict[str, DeviceRecord], observation: dict[str, str]
) -> str | None:
    """Match saved serials or MACs, rejecting advertisements with conflicting identities."""
    matches: set[str] = set()
    serial = observation.get("serial", "")
    macaddress = observation.get("macaddress", "")
    if not isinstance(serial, str) or not isinstance(macaddress, str):
        _fail("Discovery serial and MAC identifiers must be strings.")
    if serial in records:
        matches.add(serial)
    mac = _mac_key(macaddress)
    for record in records.values():
        identifiers = {
            _mac_key(record.serial),
            _mac_key(record.discovery.macaddress) if record.discovery else "",
        }
        if mac and mac in identifiers:
            matches.add(record.serial)
    if len(matches) > 1:
        _fail("Discovery identities match multiple saved devices; no updates saved.")
    return next(iter(matches), None)


def _is_link_local(host: str) -> bool:
    """Recognize link-local addresses while allowing saved DNS hostnames."""
    try:
        return ip_address(host).is_link_local
    except ValueError:
        return False


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

    def upsert(
        self,
        record: DeviceRecord,
        *,
        preserve_alias: bool = False,
        create_only: bool = False,
    ) -> None:
        """Save a complete device record while keeping unrecognized configuration fields.

        Connection/alias updates are last-writer-wins, including stale records.
        Existing discovery data is retained unless a newer snapshot is supplied.
        Use update_credentials for a credentials-only read-modify-write.
        With preserve_alias, keep the latest stored alias (empty for new
        records) and reflect it on record after the write succeeds.
        With create_only, reject an already registered serial.
        """
        record.__post_init__()
        with self._locked():
            data = self._read()
            saved = _records(data).get(record.serial)
            if create_only and saved is not None:
                _fail("This device is already saved.")
            devices = data.setdefault("devices", {})
            entry = devices.setdefault(record.serial, {})
            alias = entry.get("alias", "") if preserve_alias else record.alias
            entry.update(alias=alias, model=record.model)
            entry.setdefault("config", {}).update(asdict(record.config))
            if record.discovery is not None and (
                saved is None
                or saved.discovery is None
                or record.discovery.last_seen >= saved.discovery.last_seen
            ):
                entry.setdefault("discovery", {}).update(asdict(record.discovery))
            _records(data)
            self._write(data)
            record.alias = alias
            record.discovery = _records(data)[record.serial].discovery

    def refresh_discovery(
        self, observations: list[dict[str, str]], observed_at: datetime
    ) -> list[str]:
        """Refresh matching registrations from trusted local announcements.

        Preserve aliases, credentials, connection policy, missing metadata, and
        devices absent from the scan. Never register unknown devices. Keep a
        saved non-link-local primary when only link-local data is available;
        store that address as a fallback without attempting a connection.
        Older scans cannot overwrite newer discovery snapshots.
        """
        _validate_discovery_time(observed_at)
        records = self.load()
        if not any(_discovery_match(records, row) for row in observations):
            return []
        with self._locked():
            data = self._read()
            records = _records(data)
            candidates: list[tuple[str, DiscoverySnapshot]] = []
            names = {item.name for item in fields(DiscoverySnapshot)} - {
                "host",
                "last_seen",
            }
            for row in observations:
                serial = _discovery_match(records, row)
                if serial is not None:
                    candidates.append(
                        (
                            serial,
                            DiscoverySnapshot(
                                host=row.get("host", ""),
                                last_seen=observed_at,
                                **{key: row[key] for key in names if key in row},
                            ),
                        )
                    )
            merged: dict[str, dict[str, Any]] = {}
            for serial, snapshot in sorted(
                candidates, key=lambda item: _is_link_local(item[1].host)
            ):
                updates = {
                    key: value for key, value in asdict(snapshot).items() if value
                }
                if _is_link_local(snapshot.host):
                    updates["link_local_host"] = snapshot.host
                target = merged.setdefault(serial, {})
                for key, value in updates.items():
                    target.setdefault(key, value)
            updated: list[str] = []
            for serial, updates in merged.items():
                record = records[serial]
                if record.discovery and record.discovery.last_seen > observed_at:
                    continue
                previous = asdict(record.discovery) if record.discovery else {}
                if not previous.get("model"):
                    previous["model"] = record.model
                snapshot = DiscoverySnapshot(**(previous | updates))
                entry = data["devices"][serial]
                entry.setdefault("discovery", {}).update(asdict(snapshot))
                if "model" in updates:
                    entry["model"] = snapshot.model
                if not _is_link_local(snapshot.host) or _is_link_local(
                    record.config.host
                ):
                    entry["config"]["host"] = snapshot.host
                updated.append(serial)
            if updated:
                _records(data)
                self._write(data)
            return updated

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

    def update_settings(
        self, original: DeviceRecord, config: ConnectionSettings, alias: str
    ) -> DeviceRecord:
        """Save validated settings only if the alias and connection still match."""
        with self._locked():
            data = self._read()
            record = _records(data).get(original.serial)
            if (
                record is None
                or record.config != original.config
                or record.alias != original.alias
            ):
                _fail("Saved settings changed. Reopen Settings and try again.")
            record.config = config
            record.alias = alias
            record.__post_init__()
            entry = data["devices"][record.serial]
            entry["config"].update(asdict(config))
            entry["alias"] = alias
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
