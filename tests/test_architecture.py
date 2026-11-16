"""Test that library, service, and CLI imports stay separate and compatible."""

import ast
from importlib.util import resolve_name
from pathlib import Path

from axis.application import operations, storage
from axis.application.records import ConnectionSettings, DeviceRecord
from axis.cli import operations as legacy_operations, storage as legacy_storage

ROOT = Path(__file__).resolve().parents[1]
PRESENTATION = (
    "axis.cli",
    "axis.gui",
    "axis.web",
    "axis.__main__",
    "click",
    "prompt_toolkit",
)


def _dependencies(source: str, package: str) -> set[str]:
    dependencies: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            dependencies.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level:
                module = resolve_name("." * node.level + module, package)
            dependencies.add(module)
            dependencies.update(f"{module}.{alias.name}" for alias in node.names)
    return dependencies


def _forbidden(source: str, package: str, prefixes: tuple[str, ...]) -> set[str]:
    return {
        dependency
        for dependency in _dependencies(source, package)
        if any(
            dependency == prefix or dependency.startswith(prefix + ".")
            for prefix in prefixes
        )
    }


def test_library_and_application_dependency_direction() -> None:
    """Keep the library independent of CLI imports and services independent of UI code."""
    violations: dict[str, set[str]] = {}
    for path in (ROOT / "axis").rglob("*.py"):
        relative = path.relative_to(ROOT)
        if relative.parts[1] == "cli" or relative == Path("axis/__main__.py"):
            continue
        application = relative.parts[1] == "application"
        prefixes = PRESENTATION if application else (*PRESENTATION, "axis.application")
        package = ".".join(relative.parts[:-1])
        forbidden = _forbidden(path.read_text(), package, prefixes)
        if forbidden:
            violations[str(relative)] = forbidden
    assert not violations, violations


def test_boundaries_detect_relative_and_nested_imports() -> None:
    """Moving an import into a function or type-checking block cannot bypass policy."""
    source = """
from .. import cli
from axis import application
if TYPE_CHECKING:
    from click import Context
def helper():
    import prompt_toolkit.completion
"""
    forbidden = _forbidden(source, "axis.models", (*PRESENTATION, "axis.application"))
    assert {
        "axis.cli",
        "axis.application",
        "click",
        "prompt_toolkit.completion",
    } <= forbidden
    assert not _forbidden(
        "from axis.models.configuration import Configuration",
        "axis.application",
        PRESENTATION,
    )


def test_existing_cli_imports_reexport_shared_implementations(tmp_path: Path) -> None:
    """Previously exposed records and workflows survive extraction without copies."""
    assert legacy_operations.health is operations.health
    assert legacy_operations.OperationError is operations.OperationError
    assert legacy_storage.DeviceRegistry is storage.DeviceRegistry
    record = legacy_storage.DeviceRecord(
        "SERIAL", legacy_storage.ConnectionSettings("camera.local", "root", "secret")
    )
    assert isinstance(record, DeviceRecord)
    assert isinstance(record.config, ConnectionSettings)
    registry = legacy_storage.DeviceRegistry(tmp_path / "devices.toml")
    registry.upsert(record)
    assert registry.resolve("SERIAL") == record
