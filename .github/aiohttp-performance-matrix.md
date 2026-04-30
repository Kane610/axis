# Aiohttp Performance Evaluation Matrix

## Context

- Date: 2026-04-29
- Branch: feature/aiohttp-test-migration
- Runtime: Python 3.14.2 via `uv run`
- Host: local development machine (macOS)

## Method

Each suite was executed 3 times with `pytest --no-cov` to reduce coverage overhead and
capture relative runtime consistency.

Commands:

1. `uv run pytest --no-cov tests/test_http_client_compat.py`
2. `uv run pytest --no-cov tests/test_vapix.py tests/test_ptz.py tests/test_view_areas.py tests/test_light_control.py`
3. `uv run pytest --no-cov tests/test_vapix.py tests/test_ptz.py tests/test_view_areas.py tests/test_light_control.py tests/test_mqtt.py tests/test_pwdgrp_cgi.py tests/test_stream_profiles.py tests/test_user_groups.py tests/test_event_instances.py tests/test_port_management.py tests/test_pir_sensor_configuration.py`

## Results

| Matrix Group | Passed Tests | Run 1 (s) | Run 2 (s) | Run 3 (s) | Avg (s) | Min (s) | Max (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| compat | 10 | 0.03 | 0.03 | 0.02 | 0.03 | 0.02 | 0.03 |
| handlers | 113 | 0.42 | 0.47 | 0.46 | 0.45 | 0.42 | 0.47 |
| phase6plus | 154 | 0.58 | 0.54 | 0.55 | 0.56 | 0.54 | 0.58 |

## Interpretation

1. Aiohttp-focused integration suites remain stable and low-latency on repeated runs.
2. Runtime spread is narrow for all groups, indicating no obvious regression drift.
3. The broader migrated suite (`phase6plus`) stays under one second across all samples.

## Exit Decision

Phase 9 acceptance is met: the aiohttp performance matrix has been executed and
recorded with repeatable timing data for representative migrated suites.