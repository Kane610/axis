"""Tests for unique ID migration contract utilities."""

from axis.interfaces.events.unique_id_migration import (
    UNIQUE_ID_MIGRATION_VERSION,
    build_unique_id_alias_map,
    build_unique_id_migration_plan,
)


def test_build_unique_id_migration_plan_is_deterministic() -> None:
    """Migration plan ordering should be deterministic and idempotent."""
    input_ids = [
        "axis_onvif:Device/axis:Sensor/PIR_0",
        "axis_tns1:Device/tnsaxis:Sensor/PIR_0",
        "axis_onvif:Device/axis:Light/Status_0",
    ]

    plan = build_unique_id_migration_plan(input_ids)

    assert plan.version == UNIQUE_ID_MIGRATION_VERSION
    assert [entry.old_unique_id for entry in plan.entries] == sorted(
        [
            "axis_onvif:Device/axis:Light/Status_0",
            "axis_onvif:Device/axis:Sensor/PIR_0",
        ]
    )
    assert [entry.new_unique_id for entry in plan.entries] == [
        "axis_tns1:Device/tnsaxis:Light/Status_0",
        "axis_tns1:Device/tnsaxis:Sensor/PIR_0",
    ]


def test_build_unique_id_alias_map_returns_only_changed_entries() -> None:
    """Alias map should only include legacy IDs that require migration."""
    aliases = build_unique_id_alias_map(
        [
            "axis_tns1:Device/tnsaxis:Sensor/PIR_0",
            "axis_onvif:Device/axis:Sensor/PIR_0",
        ]
    )

    assert aliases == {
        "axis_onvif:Device/axis:Sensor/PIR_0": "axis_tns1:Device/tnsaxis:Sensor/PIR_0"
    }
