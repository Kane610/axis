"""Unique ID migration contract utilities for coordinated topic normalization."""

from __future__ import annotations

from dataclasses import dataclass
import re

UNIQUE_ID_MIGRATION_VERSION = 1


@dataclass(frozen=True)
class UniqueIdMigrationEntry:
    """Single unique ID migration mapping."""

    old_unique_id: str
    new_unique_id: str


@dataclass(frozen=True)
class UniqueIdMigrationPlan:
    """Deterministic migration plan for legacy unique IDs."""

    version: int
    entries: tuple[UniqueIdMigrationEntry, ...]


def _normalize_unique_id(unique_id: str) -> str:
    """Normalize topic namespaces inside a unique ID string."""
    # Unique IDs commonly embed topics in "<prefix>_<topic>_<suffix>" format.
    # Convert only namespace prefixes at token boundaries to avoid rewriting
    # already-canonical tokens such as "tnsaxis:".
    return re.sub(
        r"(^|[/_])axis:",
        r"\1tnsaxis:",
        re.sub(r"(^|[/_])onvif:", r"\1tns1:", unique_id),
    )


def build_unique_id_migration_plan(unique_ids: list[str]) -> UniqueIdMigrationPlan:
    """Build deterministic migration plan for mixed-format unique IDs."""
    entries = [
        UniqueIdMigrationEntry(old_unique_id=unique_id, new_unique_id=new_unique_id)
        for unique_id in sorted(set(unique_ids))
        if (new_unique_id := _normalize_unique_id(unique_id)) != unique_id
    ]

    return UniqueIdMigrationPlan(
        version=UNIQUE_ID_MIGRATION_VERSION,
        entries=tuple(entries),
    )


def build_unique_id_alias_map(unique_ids: list[str]) -> dict[str, str]:
    """Build lookup map from old unique IDs to normalized aliases."""
    plan = build_unique_id_migration_plan(unique_ids)
    return {entry.old_unique_id: entry.new_unique_id for entry in plan.entries}
