"""Focused validation, compatibility, atomicity, and locking tests for storage."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
import os
from pathlib import Path
import runpy
import threading
import tomllib
import traceback
from typing import Any
from unittest.mock import patch

import pytest
import tomli_w

from axis.cli import storage
from axis.cli.storage import (
    ConnectionSettings,
    DeviceRecord,
    DeviceRegistry,
    StorageError,
    default_config_path,
)


@pytest.fixture
def registry(tmp_path: Path) -> DeviceRegistry:
    """Use a per-test registry outside the real home directory."""
    return DeviceRegistry(tmp_path / "nested" / "config.toml")


def device(serial: str = "SERIAL", alias: str = "") -> DeviceRecord:
    """Build a representative device with credentials and default settings."""
    return DeviceRecord(
        serial, ConnectionSettings("camera.local", "root", "secret"), alias, "M123"
    )


def write_config(registry: DeviceRegistry, data: dict[str, Any]) -> None:
    """Seed legacy TOML without passing through registry validation."""
    registry.path.parent.mkdir(parents=True, exist_ok=True)
    registry.path.write_text(tomli_w.dumps(data))


def raw_config(registry: DeviceRegistry) -> dict[str, Any]:
    """Read raw TOML to verify unknown fields survive."""
    return tomllib.loads(registry.path.read_text())


def test_missing_config_has_no_side_effects(
    registry: DeviceRegistry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Lookup and loading do not create a missing configuration directory."""
    monkeypatch.setattr(Path, "home", lambda: registry.path.parent)
    assert default_config_path() == registry.path.parent / ".axis" / "config.toml"
    assert registry.load() == {}
    with pytest.raises(StorageError, match="not found"):
        registry.resolve("camera.local")
    assert not registry.path.parent.exists()


def test_roundtrip_and_exact_resolution(registry: DeviceRegistry) -> None:
    """All settings round-trip; serial/alias lookup never guesses hosts or case."""
    record = DeviceRecord(
        "SERIAL",
        ConnectionSettings(
            "2001:db8::1",
            "root",
            "secret",
            443,
            "https",
            True,
            True,
            "digest",
            True,
            True,
        ),
        "front",
        "M123",
    )
    registry.upsert(record)
    assert registry.load() == {"SERIAL": record}
    assert registry.resolve("SERIAL") == record
    assert registry.resolve("front") == record
    for identifier in ("serial", " front", "2001:db8::1", "", None):
        with pytest.raises(StorageError):
            registry.resolve(identifier)  # type: ignore[arg-type]
    assert "secret" not in repr(record)
    assert registry.remove("front") == record
    assert registry.load() == {}
    with pytest.raises(StorageError):
        registry.remove("SERIAL")


def test_legacy_and_unknown_keys(registry: DeviceRegistry) -> None:
    """Legacy defaults load and extensions survive updates and removals."""
    config = {"host": "camera", "username": "root", "password": "", "future": [1, 2]}
    data = {
        "theme": {"style": "dark"},
        "devices": {
            "OLD": {"model": "legacy", "config": config, "extra": {"value": 42}},
            "OTHER": {"config": asdict(device().config), "firmware": "v1"},
        },
    }
    write_config(registry, data)
    old = registry.resolve("OLD")
    assert old == DeviceRecord(
        "OLD", ConnectionSettings("camera", "root", ""), model="legacy"
    )
    old.alias = "legacy"
    old.config.port = 8080
    registry.upsert(old)
    updated = raw_config(registry)
    assert updated["theme"] == data["theme"]
    assert updated["devices"]["OTHER"] == data["devices"]["OTHER"]
    assert updated["devices"]["OLD"]["extra"] == {"value": 42}
    assert updated["devices"]["OLD"]["config"]["future"] == [1, 2]
    registry.remove("OLD")
    remaining = raw_config(registry)
    assert remaining["theme"] == data["theme"]
    assert remaining["devices"] == {"OTHER": data["devices"]["OTHER"]}
    write_config(registry, {"theme": "light"})
    assert registry.load() == {}
    registry.upsert(device())
    assert raw_config(registry)["theme"] == "light"


@pytest.mark.parametrize(
    "data",
    [
        {"devices": []},
        {"devices": {"SERIAL": "invalid"}},
        {"devices": {"SERIAL": {}}},
        {"devices": {"SERIAL": {"config": []}}},
        {"devices": {"SERIAL": {"config": {"host": "camera"}}}},
        {"devices": {"unknown": {"config": asdict(device().config)}}},
        {"devices": {"": {"config": asdict(device().config)}}},
        {"devices": {"SERIAL": {"config": asdict(device().config), "alias": 3}}},
        {"devices": {"SERIAL": {"config": asdict(device().config), "model": []}}},
    ],
)
def test_invalid_structures_do_not_get_overwritten(
    registry: DeviceRegistry, data: dict[str, Any]
) -> None:
    """Malformed entries are errors on reads and mutation, never empty defaults."""
    write_config(registry, data)
    before = registry.path.read_bytes()
    for operation in (
        registry.load,
        lambda: registry.upsert(device()),
        lambda: registry.remove("SERIAL"),
    ):
        with pytest.raises(StorageError):
            operation()
        assert registry.path.read_bytes() == before


def test_corrupt_config_and_read_errors_are_safe(registry: DeviceRegistry) -> None:
    """Parser and OS errors cannot expose config contents or credentials."""
    registry.path.parent.mkdir(parents=True)
    registry.path.write_text('password = "secret"\ninvalid = [')
    with pytest.raises(StorageError, match="repair invalid TOML") as error:
        registry.load()
    assert "secret" not in "".join(traceback.format_exception(error.value))
    with (
        patch.object(Path, "open", side_effect=PermissionError("secret")),
        pytest.raises(StorageError) as error,
    ):
        registry.load()
    assert "secret" not in "".join(traceback.format_exception(error.value))


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("host", ""),
        ("host", 1),
        ("host", " camera"),
        ("host", "cam era"),
        ("host", "https://camera"),
        ("host", "camera/path"),
        ("host", "camera?q"),
        ("host", "camera#f"),
        ("username", ""),
        ("username", 2),
        ("password", None),
        ("port", -1),
        ("port", 65536),
        ("port", True),
        ("port", "80"),
        ("web_proto", "ftp"),
        ("web_proto", None),
        ("auth_scheme", "other"),
        ("auth_scheme", []),
        ("verify_ssl", "false"),
        ("is_companion", 1),
        ("websocket_enabled", None),
        ("websocket_force", 0),
    ],
)
def test_connection_validation(name: str, value: object) -> None:
    """Incoming TOML fields retain types rather than silently coercing values."""
    values = asdict(device().config)
    values[name] = value
    with pytest.raises(StorageError):
        ConnectionSettings(**values)


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("serial", ""),
        ("serial", "unknown"),
        ("serial", "UNKNOWN"),
        ("serial", " SERIAL"),
        ("serial", None),
        ("alias", " front "),
        ("alias", None),
        ("model", 1),
        ("config", {}),
    ],
)
def test_record_validation(name: str, value: object) -> None:
    """Device identity is known, non-empty, and strongly typed."""
    values: dict[str, Any] = {"serial": "SERIAL", "config": device().config}
    values[name] = value
    with pytest.raises(StorageError):
        DeviceRecord(**values)


def test_mutated_record_is_revalidated(registry: DeviceRegistry) -> None:
    """Mutable dataclasses cannot bypass input validation during upsert."""
    record = device()
    record.config.port = -1
    with pytest.raises(StorageError):
        registry.upsert(record)
    assert not registry.path.parent.exists()


def test_alias_collisions_and_reassignment(registry: DeviceRegistry) -> None:
    """Duplicate aliases and aliases matching other serials fail atomically."""
    registry.upsert(device("ONE", "front"))
    before = registry.path.read_bytes()
    for record in (device("TWO", "front"), device("TWO", "ONE"), device("front")):
        with pytest.raises(StorageError, match="unique"):
            registry.upsert(record)
        assert registry.path.read_bytes() == before
    registry.upsert(device("ONE", "ONE"))
    assert registry.resolve("ONE").serial == "ONE"
    registry.upsert(device("TWO", "front"))
    assert registry.resolve("front").serial == "TWO"
    registry.upsert(device("TWO"))
    with pytest.raises(StorageError):
        registry.resolve("front")


@pytest.mark.parametrize("alias", ["same", "TWO"])
def test_ambiguous_legacy_aliases_fail_load(
    registry: DeviceRegistry, alias: str
) -> None:
    """Ambiguous stored aliases are rejected instead of choosing a device."""
    write_config(
        registry,
        {
            "devices": {
                "ONE": {"config": asdict(device().config), "alias": alias},
                "TWO": {"config": asdict(device().config), "alias": "same"},
            }
        },
    )
    with pytest.raises(StorageError, match="unique"):
        registry.resolve("ONE")


def test_private_atomic_writes(registry: DeviceRegistry) -> None:
    """New and replaced configs are 0600, even under a permissive umask."""
    previous = os.umask(0)
    try:
        registry.upsert(device())
        assert registry.path.stat().st_mode & 0o777 == 0o600
        assert (
            registry.path.with_name("config.toml.lock").stat().st_mode & 0o777 == 0o600
        )
        registry.path.chmod(0o644)
        registry.upsert(device(alias="front"))
        assert registry.path.stat().st_mode & 0o777 == 0o600
    finally:
        os.umask(previous)
    assert not list(registry.path.parent.glob("*.pending"))


@pytest.mark.parametrize("target", ["replace", "fsync", "dump", "open"])
def test_failed_write_cleanup(registry: DeviceRegistry, target: str) -> None:
    """Failed writes preserve the old config, remove pending files, and unlock."""
    registry.upsert(device())
    before = registry.path.read_bytes()
    error = TypeError("secret") if target == "dump" else OSError("secret")
    module = storage.tomli_w if target == "dump" else storage.os
    original_open = os.open

    def fail_pending(path: Path, flags: int, mode: int) -> int:
        if str(path).endswith(".pending"):
            raise error
        return original_open(path, flags, mode)

    with (
        patch.object(
            module, target, side_effect=fail_pending if target == "open" else error
        ),
        pytest.raises(StorageError) as caught,
    ):
        registry.upsert(device(alias="front"))
    assert "secret" not in "".join(traceback.format_exception(caught.value))
    assert registry.path.read_bytes() == before
    assert not list(registry.path.parent.glob("*.pending"))
    registry.upsert(device(alias="retry"))
    assert registry.resolve("retry").serial == "SERIAL"


def test_unsupported_platform_and_lock_failure(
    registry: DeviceRegistry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Unsupported locks fail explicitly; OS lock errors are safe and actionable."""
    with monkeypatch.context() as context:
        context.setattr(storage, "fcntl", None)
        with pytest.raises(StorageError, match="POSIX"):
            registry.upsert(device())
    assert not registry.path.parent.exists()
    assert storage.fcntl is not None
    with (
        patch.object(storage.fcntl, "flock", side_effect=OSError("secret")),
        pytest.raises(StorageError, match="permissions") as caught,
    ):
        registry.upsert(device())
    assert "secret" not in "".join(traceback.format_exception(caught.value))
    registry.upsert(device())


def test_non_posix_import(monkeypatch: pytest.MonkeyPatch) -> None:
    """The module remains importable without the platform-specific lock module."""
    with monkeypatch.context() as context:
        context.setattr(os, "name", "nt")
        module = runpy.run_path(storage.__file__)
    assert module["fcntl"] is None


def test_concurrent_mutations_hold_lock_until_write(registry: DeviceRegistry) -> None:
    """A second writer blocks and reloads after the first writer's commit."""
    entered = threading.Event()
    release = threading.Event()
    second_started = threading.Event()
    second_read = threading.Event()
    other = DeviceRegistry(registry.path)
    first_write = registry._write
    second_read_original = other._read

    def paused_write(data: dict[str, Any]) -> None:
        entered.set()
        assert release.wait(5)
        first_write(data)

    def observed_read() -> dict[str, Any]:
        second_read.set()
        return second_read_original()

    def second_writer() -> None:
        second_started.set()
        other.upsert(device("TWO"))

    with (
        patch.object(registry, "_write", side_effect=paused_write),
        patch.object(other, "_read", side_effect=observed_read),
        ThreadPoolExecutor(max_workers=2) as executor,
    ):
        first = executor.submit(registry.upsert, device("ONE"))
        try:
            assert entered.wait(5)
            second = executor.submit(second_writer)
            assert second_started.wait(5)
            assert not second_read.wait(0.1)
        finally:
            release.set()
        first.result(timeout=5)
        second.result(timeout=5)
    assert set(registry.load()) == {"ONE", "TWO"}
    # A registry instance created before updates must not use a stale snapshot.
    registry.remove("ONE")
    other.upsert(device("THREE"))
    assert set(registry.load()) == {"TWO", "THREE"}


def test_upsert_is_explicit_full_record_replacement(registry: DeviceRegistry) -> None:
    """Full-record upserts are last-writer-wins, not implicit partial updates."""
    registry.upsert(device())
    stale = registry.resolve("SERIAL")
    latest = registry.resolve("SERIAL")
    latest.model = "new-model"
    latest.alias = "new-alias"
    latest.config.host = "new-host"
    registry.upsert(latest)
    stale.config.username = "new-user"
    registry.upsert(stale)
    assert registry.resolve("SERIAL") == stale


def test_update_credentials_preserves_latest_fields(registry: DeviceRegistry) -> None:
    """Credential edits preserve current typed fields, unknown keys, and defaults."""
    write_config(
        registry,
        {
            "theme": "dark",
            "devices": {
                "SERIAL": {
                    "alias": "front",
                    "model": "current",
                    "metadata": [1, 2],
                    "config": {
                        "host": "current-host",
                        "username": "old",
                        "password": "old",
                        "future": "retained",
                    },
                },
            },
        },
    )
    before = raw_config(registry)
    result = registry.update_credentials("front", "new-user", "")
    expected = before
    expected["devices"]["SERIAL"]["config"].update(username="new-user", password="")
    assert raw_config(registry) == expected
    assert result == DeviceRecord(
        "SERIAL", ConnectionSettings("current-host", "new-user", ""), "front", "current"
    )
    assert registry.resolve("SERIAL") == result
    assert registry.path.stat().st_mode & 0o777 == 0o600


@pytest.mark.parametrize(
    ("identifier", "username", "password"),
    [
        ("missing", "root", "secret"),
        ("camera.local", "root", "secret"),
        ("SERIAL", "", "secret"),
        ("SERIAL", None, "secret"),
        ("SERIAL", "root", None),
    ],
)
def test_invalid_credential_update_is_atomic(
    registry: DeviceRegistry, identifier: str, username: Any, password: Any
) -> None:
    """Unresolvable identities and invalid credentials cannot change the file."""
    registry.upsert(device())
    before = registry.path.read_bytes()
    with pytest.raises(StorageError):
        registry.update_credentials(identifier, username, password)
    assert registry.path.read_bytes() == before


@pytest.mark.parametrize("field_name", ["alias", "serial"])
@pytest.mark.parametrize(
    "character",
    [
        "\t",
        "\n",
        "\r",
        "\0",
        "\x1b",
        "\x7f",
        "\x85",
        "\u202e",
        "\u2028",
        "\u2029",
        "\ud800",
    ],
)
def test_completion_identifiers_reject_unsafe_characters(
    field_name: str, character: str
) -> None:
    """Completion identifiers cannot inject delimiters, controls, or bidi text."""
    values: dict[str, Any] = {
        "serial": "SERIAL",
        "alias": "front",
        "config": device().config,
    }
    values[field_name] = f"before{character}after"
    with pytest.raises(StorageError, match="control"):
        DeviceRecord(**values)


def test_legacy_alias_control_characters_fail_load(registry: DeviceRegistry) -> None:
    """Unsafe aliases already stored on disk never reach completion callers."""
    write_config(
        registry,
        {
            "devices": {
                "SERIAL": {
                    "config": asdict(device().config),
                    "alias": "front\tinjected",
                },
            }
        },
    )
    with pytest.raises(StorageError, match="control"):
        registry.load()


def test_concurrent_credentials_update_reloads_under_lock(
    registry: DeviceRegistry,
) -> None:
    """Credential updates wait for concurrent full-record writes and retain them."""
    registry.upsert(device())
    other = DeviceRegistry(registry.path)
    latest = registry.resolve("SERIAL")
    latest.alias = "latest"
    latest.model = "new-model"
    latest.config.host = "new-host"
    latest.config.port = 8443
    latest.config.web_proto = "https"
    entered = threading.Event()
    release = threading.Event()
    second_started = threading.Event()
    second_read = threading.Event()
    original_write = registry._write
    original_read = other._read

    def paused_write(data: dict[str, Any]) -> None:
        entered.set()
        assert release.wait(5)
        original_write(data)

    def observed_read() -> dict[str, Any]:
        second_read.set()
        return original_read()

    def credential_writer() -> DeviceRecord:
        second_started.set()
        return other.update_credentials("SERIAL", "new-user", "new-password")

    with (
        patch.object(registry, "_write", side_effect=paused_write),
        patch.object(other, "_read", side_effect=observed_read),
        ThreadPoolExecutor(max_workers=2) as executor,
    ):
        first = executor.submit(registry.upsert, latest)
        try:
            assert entered.wait(5)
            second = executor.submit(credential_writer)
            assert second_started.wait(5)
            assert not second_read.wait(0.1)
        finally:
            release.set()
        first.result(timeout=5)
        result = second.result(timeout=5)
    latest.config.username = "new-user"
    latest.config.password = "new-password"
    assert result == latest
    assert registry.resolve("latest") == latest


def test_update_alias_preserves_legacy_fields_and_clears(
    registry: DeviceRegistry,
) -> None:
    """Offline alias changes leave credentials, legacy defaults, and extensions intact."""
    write_config(
        registry,
        {
            "theme": "dark",
            "devices": {
                "SERIAL": {
                    "model": "legacy",
                    "extra": [1, 2],
                    "config": {
                        "host": "camera",
                        "username": "root",
                        "password": "secret",
                        "future": "retained",
                    },
                },
            },
        },
    )
    expected = raw_config(registry)
    expected["devices"]["SERIAL"]["alias"] = "front"
    result = registry.update_alias("SERIAL", "front")
    assert raw_config(registry) == expected
    assert result == DeviceRecord(
        "SERIAL", ConnectionSettings("camera", "root", "secret"), "front", "legacy"
    )
    assert registry.resolve("front") == result
    cleared = registry.update_alias("front", "")
    expected["devices"]["SERIAL"]["alias"] = ""
    assert raw_config(registry) == expected
    assert cleared.alias == ""
    assert registry.resolve("SERIAL") == cleared
    with pytest.raises(StorageError, match="not found"):
        registry.resolve("front")
    assert registry.path.stat().st_mode & 0o777 == 0o600


@pytest.mark.parametrize(
    ("identifier", "alias"),
    [
        ("SERIAL", "existing"),
        ("SERIAL", "OTHER"),
        ("SERIAL", "bad\talias"),
        ("SERIAL", " bad "),
        ("SERIAL", None),
        ("missing", "front"),
    ],
)
def test_update_alias_rejects_invalid_changes_atomically(
    registry: DeviceRegistry, identifier: str, alias: Any
) -> None:
    """Alias collisions, unsafe names, and unknown identities cannot alter storage."""
    registry.upsert(device())
    registry.upsert(device("OTHER", "existing"))
    before = registry.path.read_bytes()
    with pytest.raises(StorageError):
        registry.update_alias(identifier, alias)
    assert registry.path.read_bytes() == before
    assert registry.update_alias("SERIAL", "SERIAL").alias == "SERIAL"


def test_concurrent_alias_update_preserves_credentials(
    registry: DeviceRegistry,
) -> None:
    """Alias changes wait for credential commits and reload the current record."""
    registry.upsert(device())
    other = DeviceRegistry(registry.path)
    entered = threading.Event()
    release = threading.Event()
    second_started = threading.Event()
    second_read = threading.Event()
    original_write = registry._write
    original_read = other._read

    def paused_write(data: dict[str, Any]) -> None:
        entered.set()
        assert release.wait(5)
        original_write(data)

    def observed_read() -> dict[str, Any]:
        second_read.set()
        return original_read()

    def alias_writer() -> DeviceRecord:
        second_started.set()
        return other.update_alias("SERIAL", "front")

    with (
        patch.object(registry, "_write", side_effect=paused_write),
        patch.object(other, "_read", side_effect=observed_read),
        ThreadPoolExecutor(max_workers=2) as executor,
    ):
        first = executor.submit(
            registry.update_credentials, "SERIAL", "new-user", "new-password"
        )
        try:
            assert entered.wait(5)
            second = executor.submit(alias_writer)
            assert second_started.wait(5)
            assert not second_read.wait(0.1)
        finally:
            release.set()
        credentials = first.result(timeout=5)
        result = second.result(timeout=5)
    assert result.config == credentials.config
    assert result.alias == "front"
    assert registry.resolve("front") == result


def test_upsert_preserve_alias_uses_latest_value(registry: DeviceRegistry) -> None:
    """Re-registration preserves current aliases but still replaces other typed fields."""
    registry.upsert(device(alias="original"))
    stale = registry.resolve("SERIAL")
    registry.update_alias("SERIAL", "latest")
    registry.update_credentials("SERIAL", "other-user", "other-password")
    stale.config.host = "new-host"
    registry.upsert(stale, preserve_alias=True)
    assert stale.alias == "latest"
    assert registry.resolve("latest") == stale
    assert stale.config.username == "root"
    registry.update_alias("SERIAL", "")
    registry.upsert(stale, preserve_alias=True)
    assert stale.alias == ""
    assert registry.resolve("SERIAL") == stale


def test_upsert_explicit_alias_replaces_or_clears(registry: DeviceRegistry) -> None:
    """Explicit alias requests remain full replacements, including empty aliases."""
    registry.upsert(device(alias="original"))
    replacement = device(alias="replacement")
    registry.upsert(replacement, preserve_alias=False)
    assert registry.resolve("replacement") == replacement
    cleared = device()
    registry.upsert(cleared)
    assert registry.resolve("SERIAL") == cleared
    with pytest.raises(StorageError, match="not found"):
        registry.resolve("replacement")


@pytest.mark.parametrize("incoming_alias", ["", "ignored"])
def test_upsert_preserve_alias_on_new_device_is_empty(
    registry: DeviceRegistry, incoming_alias: str
) -> None:
    """An unspecified alias on a newly registered device defaults to empty."""
    record = device(alias=incoming_alias)
    registry.upsert(record, preserve_alias=True)
    assert record.alias == ""
    assert registry.resolve("SERIAL") == record


def test_concurrent_upsert_preserves_alias_committed_under_lock(
    registry: DeviceRegistry,
) -> None:
    """Re-registration reloads aliases after a concurrent alias writer commits."""
    registry.upsert(device(alias="original"))
    other = DeviceRegistry(registry.path)
    registration = device()
    registration.config.host = "new-host"
    entered = threading.Event()
    release = threading.Event()
    second_started = threading.Event()
    second_read = threading.Event()
    original_write = registry._write
    original_read = other._read

    def paused_write(data: dict[str, Any]) -> None:
        entered.set()
        assert release.wait(5)
        original_write(data)

    def observed_read() -> dict[str, Any]:
        second_read.set()
        return original_read()

    def registration_writer() -> None:
        second_started.set()
        other.upsert(registration, preserve_alias=True)

    with (
        patch.object(registry, "_write", side_effect=paused_write),
        patch.object(other, "_read", side_effect=observed_read),
        ThreadPoolExecutor(max_workers=2) as executor,
    ):
        first = executor.submit(registry.update_alias, "SERIAL", "latest")
        try:
            assert entered.wait(5)
            second = executor.submit(registration_writer)
            assert second_started.wait(5)
            assert not second_read.wait(0.1)
        finally:
            release.set()
        first.result(timeout=5)
        second.result(timeout=5)
    assert registration.alias == "latest"
    assert registry.resolve("latest") == registration
