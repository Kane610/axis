"""Inspect local ACAP application packages without executing or extracting them."""

from dataclasses import asdict, dataclass
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import stat
import tarfile
from typing import IO, Any, Literal, Protocol
import zlib

MAX_PACKAGE_SIZE = 1024 * 1024 * 1024
MAX_EXPANDED_SIZE = 256 * 1024 * 1024
MAX_METADATA_SIZE = 1024 * 1024
MAX_ARCHIVE_MEMBERS = 10000
MAX_PACKAGES = 1000
SIGNATURE_MAGIC = bytes.fromhex("658d14ab4207aac6")
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


@dataclass(frozen=True)
class Package:
    """Metadata read from an ACAP package; signatures are not verified."""

    filename: str
    digest: str
    size: int
    name: str
    friendly_name: str
    version: str
    architecture: str
    vendor: str
    vendor_id: str
    os_ranges: tuple[tuple[str, str], ...]
    sdk: str
    signature: str
    schema_version: str | None = ""

    def public(self) -> dict[str, Any]:
        """Return JSON-compatible metadata."""
        return asdict(self)


class PackageError(ValueError):
    """A package cannot be safely inspected."""


class _Reader(Protocol):
    def read(self, size: int = -1) -> bytes: ...


class _LimitedReader(io.RawIOBase):
    def __init__(self, source: _Reader) -> None:
        super().__init__()
        self.source = source
        self.remaining = MAX_EXPANDED_SIZE

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            size = self.remaining + 1
        if size > self.remaining:
            msg = "Package expands beyond the inspection limit."
            raise PackageError(msg)
        data = self.source.read(size)
        self.remaining -= len(data)
        return data


def _signature(package: IO[bytes], size: int) -> str:
    if size < 16:
        return "unknown"
    package.seek(-16, os.SEEK_END)
    footer = package.read(16)
    if footer[8:] != SIGNATURE_MAGIC:
        package.seek(0)
        if package.read(2) != b"\x1f\x8b":
            return "unknown"
        package.seek(0)
        decoder = zlib.decompressobj(31)
        remaining = MAX_EXPANDED_SIZE
        try:
            while True:
                data = package.read(65536)
                if not data:
                    msg = "Incomplete gzip package."
                    raise PackageError(msg)
                while data:
                    decoded = decoder.decompress(data, min(remaining + 1, 1048576))
                    remaining -= len(decoded)
                    if remaining < 0:
                        msg = "Package expands beyond the inspection limit."
                        raise PackageError(msg)
                    data = decoder.unconsumed_tail
                    if decoder.eof:
                        break
                if decoder.eof:
                    break
        except zlib.error as exc:
            msg = "Invalid gzip package."
            raise PackageError(msg) from exc
        return (
            "not_detected"
            if not decoder.unused_data and not package.read(1)
            else "unknown"
        )
    length = int.from_bytes(footer[:4], "big")
    if (
        int.from_bytes(footer[4:8], "big") != 1
        or length < 1
        or length > MAX_METADATA_SIZE
        or length + 16 > size
    ):
        msg = "Invalid signature footer."
        raise PackageError(msg)
    package.seek(-(length + 16), os.SEEK_END)
    signature = package.read(length)
    if not (
        signature.startswith(b"-----BEGIN PGP SIGNATURE-----")
        and signature.rstrip().endswith(b"-----END PGP SIGNATURE-----")
    ):
        msg = "Invalid signature block."
        raise PackageError(msg)
    return "present_unverified"


def _archive_metadata(package: IO[bytes]) -> tuple[bytes | None, bytes | None]:
    package.seek(0)
    found: dict[str, bytes] = {}
    if package.read(2) == b"\x1f\x8b":
        package.seek(0)
        source: _Reader = gzip.GzipFile(fileobj=package)
    else:
        package.seek(0)
        source = package
    try:
        reader = _LimitedReader(source)
        with tarfile.open(fileobj=reader, mode="r|") as archive:
            for count, member in enumerate(archive, start=1):
                if count > MAX_ARCHIVE_MEMBERS:
                    msg = "Package has too many archive entries."
                    raise PackageError(msg)
                member_path = PurePosixPath(member.name)
                if member_path.is_absolute() or ".." in member_path.parts:
                    msg = "Package contains an unsafe archive path."
                    raise PackageError(msg)
                name = str(member_path)
                if name not in {"manifest.json", "package.conf"}:
                    continue
                if (
                    name in found
                    or not member.isfile()
                    or member.size > MAX_METADATA_SIZE
                ):
                    msg = "Package metadata is ambiguous or too large."
                    raise PackageError(msg)
                entry = archive.extractfile(member)
                if entry is None:
                    msg = "Cannot read package metadata."
                    raise PackageError(msg)
                found[name] = entry.read(MAX_METADATA_SIZE + 1)
    finally:
        if isinstance(source, gzip.GzipFile):
            source.close()
    return found.get("manifest.json"), found.get("package.conf")


def _field(data: dict[str, Any], key: str) -> str:
    value = data.get(key, "")
    if not isinstance(value, str) or len(value) > 1024:
        msg = "Invalid package metadata."
        raise PackageError(msg)
    return value


def _legacy(data: bytes | None) -> dict[str, str]:
    if data is None:
        return {}
    result: dict[str, str] = {}
    for line in data.decode("utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition("=")
        if not separator or not re.fullmatch(r"[A-Z][A-Z0-9_]*", key):
            msg = "Invalid legacy package metadata."
            raise PackageError(msg)
        try:
            values = shlex.split(value, comments=True)
        except ValueError as exc:
            msg = "Invalid legacy package metadata."
            raise PackageError(msg) from exc
        if len(values) > 1 or key in result:
            msg = "Invalid legacy package metadata."
            raise PackageError(msg)
        result[key] = values[0] if values else ""
    return result


def _metadata(
    manifest: bytes | None, legacy_data: bytes | None
) -> tuple[dict[str, Any], tuple[tuple[str, str], ...], str | None]:
    if manifest is None:
        legacy = _legacy(legacy_data)
        return (
            {
                "appName": legacy.get("APPNAME", ""),
                "friendlyName": legacy.get("PACKAGENAME", ""),
                "version": ".".join(
                    legacy.get(key, "")
                    for key in ("APPMAJORVERSION", "APPMINORVERSION", "APPMICROVERSION")
                ),
                "architecture": legacy.get("APPTYPE", ""),
                "vendor": legacy.get("VENDOR", ""),
                "embeddedSdkVersion": legacy.get("REQEMBDEVVERSION", ""),
            },
            (),
            None,
        )
    data = json.loads(manifest)
    if not isinstance(data, dict) or not isinstance(data.get("acapPackageConf"), dict):
        msg = "Invalid ACAP manifest."
        raise PackageError(msg)
    setup = data["acapPackageConf"].get("setup")
    if not isinstance(setup, dict):
        msg = "Invalid ACAP manifest setup."
        raise PackageError(msg)
    if legacy_data is not None:
        legacy = _legacy(legacy_data)
        name = legacy.get("APPNAME", "")
        if name and name != _field(setup, "appName"):
            msg = "Manifest and package.conf identify different applications."
            raise PackageError(msg)
        legacy_version = [
            legacy.get(key, "")
            for key in ("APPMAJORVERSION", "APPMINORVERSION", "APPMICROVERSION")
        ]
        if all(legacy_version) and ".".join(legacy_version) != _field(setup, "version"):
            msg = "Manifest and package.conf have different versions."
            raise PackageError(msg)
    ranges = setup.get("compatibleOsVersions", [])
    if not isinstance(ranges, list) or len(ranges) > 100:
        msg = "Invalid compatible OS versions."
        raise PackageError(msg)
    versions = []
    for item in ranges:
        if not isinstance(item, dict):
            msg = "Invalid compatible OS versions."
            raise PackageError(msg)
        versions.append((_field(item, "min"), _field(item, "max")))
    return setup, tuple(versions), _field(data, "schemaVersion")


def inspect_package(package: IO[bytes], filename: str) -> Package:
    """Inspect an open, seekable package without trusting its filename."""
    before = os.fstat(package.fileno())
    if not stat.S_ISREG(before.st_mode) or not 0 < before.st_size <= MAX_PACKAGE_SIZE:
        msg = "Package must be a non-empty regular file up to 1 GiB."
        raise PackageError(msg)
    try:
        signature = _signature(package, before.st_size)
        manifest, legacy = _archive_metadata(package)
        if manifest is None and legacy is None:
            msg = "No ACAP manifest or package.conf found."
            raise PackageError(msg)
        setup, ranges, schema_version = _metadata(manifest, legacy)
        package.seek(0)
        hasher = hashlib.sha256()
        while chunk := package.read(262144):
            hasher.update(chunk)
        digest = hasher.hexdigest()
        after = os.fstat(package.fileno())
        if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ):
            msg = "Package changed during inspection."
            raise PackageError(msg)
        return Package(
            filename=filename,
            digest=digest,
            size=before.st_size,
            name=_field(setup, "appName"),
            friendly_name=_field(setup, "friendlyName"),
            version=_field(setup, "version"),
            architecture=_field(setup, "architecture"),
            vendor=_field(setup, "vendor"),
            vendor_id=_field(setup, "vendorId"),
            os_ranges=ranges,
            sdk=_field(setup, "embeddedSdkVersion"),
            signature=signature,
            schema_version=schema_version,
        )
    except (
        OSError,
        EOFError,
        tarfile.TarError,
        UnicodeError,
        json.JSONDecodeError,
    ) as exc:
        msg = "Cannot read ACAP package metadata."
        raise PackageError(msg) from exc


def open_package(folder: str, filename: str) -> IO[bytes]:
    """Open one regular package under the configured directory, never a symlink."""
    if (
        not filename
        or filename in {".", ".."}
        or Path(filename).name != filename
        or "\\" in filename
        or not filename.lower().endswith(".eap")
    ):
        msg = "Invalid package filename."
        raise PackageError(msg)
    try:
        descriptor = os.open(
            Path(folder) / filename, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
        )
        return os.fdopen(descriptor, "rb")
    except OSError as exc:
        msg = "Cannot open package; check folder permissions."
        raise PackageError(msg) from exc


def scan_folder(folder: str | None) -> dict[str, Any]:
    """Inspect packages in the configured folder and report individual failures."""
    if folder is None:
        return {"packages": [], "errors": []}
    paths = []
    try:
        with os.scandir(folder) as entries:
            for entry in entries:
                if entry.name.lower().endswith(".eap"):
                    paths.append(entry.name)
                    if len(paths) > MAX_PACKAGES:
                        msg = "ACAP folder contains too many packages."
                        raise PackageError(msg)
    except OSError as exc:
        msg = "Cannot read ACAP folder; check its path and permissions."
        raise PackageError(msg) from exc
    packages = []
    errors = []
    for filename in sorted(paths):
        try:
            with open_package(folder, filename) as package:
                packages.append(inspect_package(package, filename).public())
        except PackageError as exc:
            errors.append({"filename": filename, "message": str(exc)})
    return {"packages": packages, "errors": errors}


def version_key(value: str) -> tuple[Any, ...] | None:
    """Return a semantic-version ordering key, or None for unknown formats."""
    match = SEMVER.fullmatch(value)
    if not match:
        return None
    prerelease = match.group(4)
    parts: list[tuple[int, int | str]] = []
    if prerelease:
        for item in prerelease.split("."):
            if item.isdigit():
                if len(item) > 1 and item.startswith("0"):
                    return None
                parts.append((0, int(item)))
            else:
                parts.append((1, item))
    return (
        int(match.group(1)),
        int(match.group(2)),
        int(match.group(3)),
        0 if prerelease else 1,
        tuple(parts),
    )


def _os_version(
    value: str, *, upper: bool = False
) -> tuple[int | float, int | float, int | float] | None:
    if not re.fullmatch(r"\d+(?:\.\d+){0,2}", value):
        return None
    parts: list[int | float] = [int(part) for part in value.split(".")]
    parts.extend([float("inf") if upper else 0] * (3 - len(parts)))
    return parts[0], parts[1], parts[2]


@dataclass(frozen=True)
class AssessmentFinding:
    """A compatibility finding and how much is known about it."""

    kind: Literal["incompatible", "unknown", "not_checked", "review"]
    message: str


@dataclass(frozen=True)
class UpdateAssessment:
    """Warnings and ordering for a manually confirmed package change."""

    findings: tuple[AssessmentFinding, ...]
    severity: int
    downgrade: bool

    @property
    def warnings(self) -> tuple[str, ...]:
        """Return findings that must be acknowledged when confirming a write."""
        return tuple(
            finding.message
            for finding in self.findings
            if finding.kind != "not_checked"
        )


def _assess_environment(
    package: Package,
    architecture: str,
    os_version: str,
    allow_unsigned: bool | None,
) -> UpdateAssessment | None:
    if (
        architecture
        and package.architecture
        and package.architecture
        not in {
            architecture,
            "all",
        }
    ):
        return None

    findings: list[AssessmentFinding] = []
    severity = 0
    if not architecture or not package.architecture:
        findings.append(
            AssessmentFinding("unknown", "Architecture compatibility is unknown.")
        )
        severity = max(severity, 1)
    device_os = _os_version(os_version)
    bounds = [
        (_os_version(low), _os_version(high, upper=True))
        for low, high in package.os_ranges
    ]
    schema = version_key(package.schema_version) if package.schema_version else None
    schema_major = schema[0] if schema else None
    if schema_major == 2 and not re.fullmatch(r"[0-9a-fA-F]{10}", package.vendor_id):
        findings.append(
            AssessmentFinding(
                "incompatible",
                "Manifest schema 2 requires a vendor ID of ten hexadecimal characters.",
            )
        )
        severity = 2
    if schema_major != 2:
        reason = (
            "legacy package metadata does not declare OS ranges"
            if package.schema_version is None
            else "manifest schema 1 does not declare OS ranges"
            if schema_major == 1
            else "the manifest schema is missing or not recognized"
        )
        findings.append(
            AssessmentFinding("unknown", f"AXIS OS compatibility is unknown: {reason}.")
        )
        severity = max(severity, 1)
        if package.schema_version is None or schema_major == 1:
            findings.append(
                AssessmentFinding(
                    "not_checked", "Legacy SDK compatibility has not been checked."
                )
            )
    elif not bounds or any(
        low is None or high is None or low > high for low, high in bounds
    ):
        findings.append(
            AssessmentFinding(
                "incompatible",
                "Manifest schema 2 requires valid AXIS OS version ranges.",
            )
        )
        severity = 2
    elif device_os is None:
        findings.append(
            AssessmentFinding(
                "unknown",
                "AXIS OS compatibility is unknown: the device version is unavailable or unrecognized.",
            )
        )
        severity = max(severity, 1)
    elif not any(
        low <= device_os <= high
        for low, high in bounds
        if low is not None and high is not None
    ):
        message = "AXIS OS version is outside the package's declared ranges."
        if device_os >= (12, 10, 0):
            message += " The device is expected to reject installation."
        findings.append(AssessmentFinding("incompatible", message))
        severity = 2
    if package.signature != "present_unverified":
        findings.append(
            AssessmentFinding(
                "unknown",
                "No supported signature was detected."
                if package.signature == "not_detected"
                else "Package signature format is unknown.",
            )
        )
        severity = max(severity, 1)
    else:
        findings.append(
            AssessmentFinding(
                "not_checked",
                "Package signature is present but has not been verified locally.",
            )
        )
    if allow_unsigned is None:
        findings.append(
            AssessmentFinding("unknown", "Unsigned application policy is unknown.")
        )
        severity = max(severity, 1)
    elif not allow_unsigned and package.signature != "present_unverified":
        findings.append(
            AssessmentFinding(
                "review",
                "Unsigned applications are disabled; the device may reject this package.",
            )
        )
        severity = 2
    return UpdateAssessment(tuple(findings), severity, False)


def assess_update(
    package: Package,
    name: str,
    version: str,
    architecture: str,
    os_version: str,
    allow_unsigned: bool | None,
    vendor: str = "",
) -> UpdateAssessment | None:
    """Assess a package without treating warnings as permission to install it."""
    if package.name != name:
        return None
    environment = _assess_environment(package, architecture, os_version, allow_unsigned)
    if environment is None:
        return None
    findings: list[AssessmentFinding] = []
    severity = 0
    current, candidate = version_key(version), version_key(package.version)
    downgrade = current is not None and candidate is not None and candidate < current
    if current is None or candidate is None:
        findings.append(
            AssessmentFinding(
                "unknown",
                "Application version cannot be compared; this may be a downgrade.",
            )
        )
        severity = 2
    elif candidate == current:
        return None
    elif downgrade:
        findings.append(AssessmentFinding("review", "This is a downgrade."))

    if not vendor.strip() or not package.vendor.strip():
        findings.append(AssessmentFinding("unknown", "Vendor name cannot be compared."))
        severity = max(severity, 1)
    elif vendor.strip().casefold() != package.vendor.strip().casefold():
        findings.append(
            AssessmentFinding(
                "review", "Vendor differs from the installed application."
            )
        )
        severity = 2
    findings.append(
        AssessmentFinding(
            "not_checked",
            "The installed application's vendor ID is unavailable; the device may reject the upgrade even if vendor names match.",
        )
    )
    return UpdateAssessment(
        tuple(findings) + environment.findings,
        max(severity, environment.severity),
        downgrade,
    )


def assess_install(
    package: Package, architecture: str, os_version: str, allow_unsigned: bool | None
) -> UpdateAssessment | None:
    """Assess a package for a new installation without assuming vendor identity."""
    if not package.name.strip():
        return None
    environment = _assess_environment(package, architecture, os_version, allow_unsigned)
    if environment is None:
        return None
    findings = [
        AssessmentFinding(
            "not_checked", "Package vendor identity has not been verified."
        )
    ]
    severity = 0
    if not package.vendor.strip():
        findings.append(AssessmentFinding("unknown", "Package vendor is unknown."))
        severity = 1
    if version_key(package.version) is None:
        findings.append(
            AssessmentFinding(
                "unknown", "Package version is unknown or cannot be interpreted."
            )
        )
        severity = 1
    return UpdateAssessment(
        tuple(findings) + environment.findings,
        max(severity, environment.severity),
        False,
    )
