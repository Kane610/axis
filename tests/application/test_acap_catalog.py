"""Exercise safe ACAP package inspection and update compatibility."""

from dataclasses import replace
from io import BytesIO
import json
import tarfile
from typing import TYPE_CHECKING

import pytest

from axis.application import acap_catalog as catalog

if TYPE_CHECKING:
    from pathlib import Path


def create_package(
    path: Path,
    setup: dict[str, object] | None = None,
    *,
    signed: bool = False,
    compressed: bool = True,
    entries: list[tuple[str, bytes]] | None = None,
) -> None:
    """Build a small archive with the observed ACAP package layout."""
    if entries is None:
        manifest = {
            "schemaVersion": "2.1.0",
            "acapPackageConf": {
                "setup": setup
                or {
                    "appName": "example",
                    "friendlyName": "Example",
                    "version": "2.0.0",
                    "architecture": "armv7hf",
                    "vendor": "Vendor",
                    "vendorId": "123",
                    "compatibleOsVersions": [{"min": "12.10", "max": "13"}],
                }
            },
        }
        entries = [("manifest.json", json.dumps(manifest).encode())]
    with tarfile.open(path, "w:gz" if compressed else "w") as archive:
        for name, data in entries:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            archive.addfile(info, BytesIO(data))
    if signed:
        signature = (
            b"-----BEGIN PGP SIGNATURE-----\nexample\n-----END PGP SIGNATURE-----\n"
        )
        with path.open("ab") as package:
            package.write(signature)
            package.write(len(signature).to_bytes(4, "big"))
            package.write((1).to_bytes(4, "big"))
            package.write(catalog.SIGNATURE_MAGIC)


def read(path: Path) -> catalog.Package:
    """Inspect a test package."""
    with path.open("rb") as package:
        return catalog.inspect_package(package, path.name)


def test_inspects_signed_unsigned_and_plain_packages(tmp_path: Path) -> None:
    """Identify observed signature markers without claiming verification."""
    signed = tmp_path / "signed.eap"
    unsigned = tmp_path / "unsigned.eap"
    plain = tmp_path / "plain.eap"
    create_package(signed, signed=True)
    create_package(unsigned)
    create_package(plain, compressed=False)
    result = read(signed)
    assert result.name == "example"
    assert result.version == "2.0.0"
    assert result.architecture == "armv7hf"
    assert result.os_ranges == (("12.10", "13"),)
    assert result.signature == "present_unverified"
    assert read(unsigned).signature == "not_detected"
    assert read(plain).signature == "unknown"
    assert result.digest != read(unsigned).digest


def test_scans_legacy_and_reports_invalid_and_symlink(
    tmp_path: Path,
) -> None:
    """Parse legacy metadata and report invalid entries independently."""
    legacy = tmp_path / "legacy.eap"
    create_package(
        legacy,
        entries=[
            (
                "package.conf",
                (
                    b'APPNAME="legacy"\nPACKAGENAME="Legacy"\nAPPTYPE="armv7hf"\n'
                    b'APPMAJORVERSION="1"\nAPPMINORVERSION="2"\nAPPMICROVERSION="3"\n'
                ),
            )
        ],
    )
    (tmp_path / "bad.eap").write_bytes(b"not an archive")
    (tmp_path / "link.eap").symlink_to(legacy)
    result = catalog.scan_folder(str(tmp_path))
    assert result["packages"][0]["name"] == "legacy"
    assert result["packages"][0]["version"] == "1.2.3"
    assert {error["filename"] for error in result["errors"]} == {"bad.eap", "link.eap"}
    with pytest.raises(catalog.PackageError, match="filename"):
        catalog.open_package(str(tmp_path), "../legacy.eap")


@pytest.mark.parametrize(
    "entries",
    [
        [("other", b"no metadata")],
        [("manifest.json", b"not json")],
        [("manifest.json", b"{}")],
        [("manifest.json", b"{}"), ("manifest.json", b"{}")],
        [("package.conf", b'APPNAME="unfinished')],
        [("package.conf", b"APPNAME=one two")],
        [("package.conf", b"APPNAME=one\nAPPNAME=two")],
    ],
)
def test_rejects_malformed_metadata(
    tmp_path: Path, entries: list[tuple[str, bytes]]
) -> None:
    """Reject missing, malformed, or ambiguous metadata."""
    path = tmp_path / "bad.eap"
    create_package(path, entries=entries)
    with pytest.raises(catalog.PackageError):
        read(path)


@pytest.mark.parametrize(
    "setup",
    [
        {"appName": 123},
        {"appName": "x" * 1025},
        {"compatibleOsVersions": "12"},
        {"compatibleOsVersions": [123]},
        {"compatibleOsVersions": [{"min": 12, "max": "13"}]},
    ],
)
def test_rejects_invalid_manifest_fields(
    tmp_path: Path, setup: dict[str, object]
) -> None:
    """Malformed identity and compatibility fields never become candidates."""
    path = tmp_path / "package.eap"
    create_package(path, setup)
    with pytest.raises(catalog.PackageError):
        read(path)


@pytest.mark.parametrize("name", ["../manifest.json", "/manifest.json"])
def test_rejects_archive_path_traversal(tmp_path: Path, name: str) -> None:
    """Do not classify packages whose archive paths escape their root."""
    path = tmp_path / "unsafe.eap"
    create_package(path, entries=[(name, b"{}")])
    with pytest.raises(catalog.PackageError, match="unsafe archive path"):
        read(path)


def test_rejects_duplicate_alias_and_nonregular_metadata(tmp_path: Path) -> None:
    """Do not interpret conflicting or linked metadata as a valid manifest."""
    path = tmp_path / "duplicate.eap"
    create_package(path, entries=[("manifest.json", b"{}"), ("./manifest.json", b"{}")])
    with pytest.raises(catalog.PackageError, match="ambiguous"):
        read(path)
    with tarfile.open(path, "w:gz") as archive:
        entry = tarfile.TarInfo("manifest.json")
        entry.type = tarfile.SYMTYPE
        entry.linkname = "other"
        archive.addfile(entry)
    with pytest.raises(catalog.PackageError, match="ambiguous"):
        read(path)


@pytest.mark.parametrize(
    "legacy",
    [
        b'APPNAME="other"\n',
        b'APPNAME="example"\nAPPMAJORVERSION="3"\nAPPMINORVERSION="0"\nAPPMICROVERSION="0"\n',
    ],
)
def test_rejects_conflicting_manifest_and_legacy_identity(
    tmp_path: Path, legacy: bytes
) -> None:
    """Prevent a package from identifying different apps or versions on older firmware."""
    path = tmp_path / "conflict.eap"
    manifest = json.dumps(
        {"acapPackageConf": {"setup": {"appName": "example", "version": "2.0.0"}}}
    ).encode()
    create_package(
        path, entries=[("manifest.json", manifest), ("package.conf", legacy)]
    )
    with pytest.raises(catalog.PackageError, match="different"):
        read(path)


def test_rejects_invalid_signature_and_limits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Reject malformed signature footers and excessive expansion."""
    path = tmp_path / "package.eap"
    create_package(path, signed=True)
    with path.open("r+b") as package:
        package.seek(-12, 2)
        package.write((3).to_bytes(4, "big"))
    with pytest.raises(catalog.PackageError, match="signature footer"):
        read(path)
    create_package(path)
    monkeypatch.setattr(catalog, "MAX_EXPANDED_SIZE", 512)
    with pytest.raises(catalog.PackageError, match="inspection limit"):
        read(path)


def test_rejects_invalid_and_truncated_compressed_packages(tmp_path: Path) -> None:
    """Report invalid gzip data, truncated streams, and malformed signatures."""
    path = tmp_path / "broken.eap"
    path.write_bytes(b"\x1f\x8b" + b"\x00" * 64)
    with pytest.raises(catalog.PackageError, match="gzip"):
        read(path)
    create_package(path)
    data = path.read_bytes()
    path.write_bytes(data[:-8])
    with pytest.raises(catalog.PackageError, match="Incomplete gzip"):
        read(path)
    create_package(path, signed=True)
    data = path.read_bytes()
    signature_start = data.index(b"-----BEGIN PGP SIGNATURE-----")
    path.write_bytes(data[:signature_start] + b"X" + data[signature_start + 1 :])
    with pytest.raises(catalog.PackageError, match="signature block"):
        read(path)
    create_package(path)
    with path.open("ab") as package:
        package.write(b"unknown trailer")
    assert read(path).signature == "unknown"


def test_scan_bounds_and_missing_folder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Bound metadata and catalog sizes, and expose inaccessible directories."""
    path = tmp_path / "example.eap"
    create_package(path)
    with pytest.raises(catalog.PackageError, match="Cannot read ACAP folder"):
        catalog.scan_folder(str(tmp_path / "missing"))
    monkeypatch.setattr(catalog, "MAX_METADATA_SIZE", 32)
    with pytest.raises(catalog.PackageError, match="metadata"):
        read(path)
    monkeypatch.setattr(catalog, "MAX_PACKAGES", 0)
    with pytest.raises(catalog.PackageError, match="too many"):
        catalog.scan_folder(str(tmp_path))


def test_semver_and_device_compatibility(tmp_path: Path) -> None:
    """Assess each risk while excluding other apps and known architecture mismatches."""
    path = tmp_path / "package.eap"
    create_package(path, signed=True)
    package = read(path)
    assert catalog.version_key("1.0.0-alpha.2") < catalog.version_key("1.0.0-alpha.10")
    assert catalog.version_key("1.0.0-alpha") < catalog.version_key("1.0.0")
    assert catalog.version_key("1.0.0-01") is None
    assessment = catalog.assess_update(
        package, "example", "1.0.0", "armv7hf", "12.10.3", False, "Vendor"
    )
    assert assessment is not None
    assert assessment.warnings == ()
    assert not assessment.downgrade
    assert (
        catalog.assess_update(package, "other", "1.0.0", "armv7hf", "12.10", False)
        is None
    )
    assert (
        catalog.assess_update(package, "example", "2.0.0", "armv7hf", "12.10", False)
        is None
    )
    assert (
        catalog.assess_update(package, "example", "1.0.0", "aarch64", "12.10", False)
        is None
    )
    assessment = catalog.assess_update(
        replace(package, os_ranges=(("bad", "13"),), signature="not_detected"),
        "example",
        "unknown",
        "",
        "12.10",
        False,
        "Other",
    )
    assert assessment is not None
    assert assessment.warnings == (
        "Application version cannot be compared; this may be a downgrade.",
        "Vendor differs from the installed application.",
        "Architecture compatibility is unknown.",
        "AXIS OS compatibility is unknown.",
        "No signature was detected.",
        "Unsigned applications are disabled on the device.",
    )
    assessment = catalog.assess_update(
        package, "example", "3.0.0", "armv7hf", "14.0", None
    )
    assert assessment is not None
    assert assessment.downgrade
    assert "This is a downgrade." in assessment.warnings
    assert "Vendor identity cannot be compared." in assessment.warnings
    assert "AXIS OS version is outside the package ranges." in assessment.warnings
    assert "Unsigned application policy is unknown." in assessment.warnings


def test_new_install_assessment_does_not_assume_an_existing_version(
    tmp_path: Path,
) -> None:
    """Assess unknown metadata and hide packages with no identity or wrong hardware."""
    path = tmp_path / "package.eap"
    create_package(path, signed=True)
    package = read(path)
    assessment = catalog.assess_install(package, "armv7hf", "12.10", False)
    assert assessment is not None
    assert assessment.warnings == (
        "Vendor identity cannot be compared to an installed application.",
    )
    assessment = catalog.assess_install(
        replace(package, version="", vendor="", signature="unknown"),
        "",
        "12.10",
        None,
    )
    assert assessment is not None
    assert assessment.warnings == (
        "Vendor identity cannot be compared to an installed application.",
        "Package vendor is unknown.",
        "Package version is unknown or cannot be interpreted.",
        "Architecture compatibility is unknown.",
        "Package signature format is unknown.",
        "Unsigned application policy is unknown.",
    )
    assert (
        catalog.assess_install(replace(package, name=""), "armv7hf", "12.10", False)
        is None
    )
    assert catalog.assess_install(package, "aarch64", "12.10", False) is None
