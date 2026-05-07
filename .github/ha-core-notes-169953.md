# HA Core Notes: Axis Websocket SSL Regression (Issue #169953)

## Summary

Home Assistant Core 2026.5 enabled websocket event usage for Axis devices when supported.
In HTTPS setups that use self-signed or private-CA certificates, websocket startup could fail with certificate verification errors and repeatedly retry without falling back to RTSP event transport.

## Root Cause

The websocket transport created a separate aiohttp session for websocket connections.
That path did not reliably inherit SSL/certificate behavior from the configured Axis device session used by the rest of the integration.

## Changes in This Patch

1. Websocket now reuses the existing configured aiohttp session.
2. Runtime websocket connect failures are classified.
3. Certificate verification failures trigger runtime websocket disable and fallback to RTSP event transport (unless websocket is forced).
4. Websocket force mode remains authoritative and does not auto-downgrade.

## Expected Runtime Behavior

- If websocket startup succeeds, websocket event transport is used.
- If websocket startup fails due to SSL certificate verification and websocket is not forced, Axis falls back to RTSP event stream behavior for the remainder of the runtime.
- If websocket is forced, retries continue on websocket as configured.

## Integration Guidance for Home Assistant Core

1. Preserve current user-facing SSL semantics in config flows and options.
2. Consider exposing a repair/diagnostic message when fallback is caused by certificate verification failure.
3. Include host and reason in diagnostics to aid troubleshooting of private CA trust chains.
4. Keep websocket-force behavior opt-in and explicit.

## Validation

Targeted validation used for this patch:

- `uv run pytest tests/test_websocket.py tests/test_stream_manager.py`
- `uv run ruff check axis tests`
- `uv run ruff format --check axis tests`
