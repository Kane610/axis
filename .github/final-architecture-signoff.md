# Final Architecture Sign-Off And Rollback Gates

## Decision Summary

The aiohttp-first migration architecture is approved for completion based on:

1. Test-layer migration from dual-client coupling to aiohttp_server parity coverage.
2. Consolidated shared shim utilities for migrated suites.
3. Runtime client-simplification implementation plan documented and scoped.
4. Performance matrix confirming stable runtime behavior on representative suites.

## Signed-Off Architecture State

1. Initialization model remains phase-driven:
- API_DISCOVERY
- PARAM_CGI_FALLBACK
- APPLICATION

2. Handler registration and grouped initialization behavior are preserved.

3. Request/response behavior parity is maintained across migrated tests:
- status-code error translation,
- auth fallback behavior,
- namespace-aware/event parsing expectations.

4. Planned runtime simplification is constrained and reversible:
- move to aiohttp-only runtime sessions,
- preserve existing request error semantics,
- preserve auth retry behavior for AUTO mode.

## Release Gates

All gates must be green before rollout:

1. Linting: `uv run ruff check .`
2. Formatting: `uv run ruff format --check .`
3. Typing: `uv run mypy axis`
4. Tests: `uv run pytest`
5. Migration docs current:
- `.github/aiohttp-performance-matrix.md`

## Rollback Gates And Triggers

Rollback to pre-change baseline is required if any trigger occurs after runtime
client simplification implementation begins:

1. Functional trigger:
- auth negotiation failures or increased 401/403 responses in supported devices.

2. Reliability trigger:
- sustained request timeout/connection-error regression outside historical bounds.

3. Compatibility trigger:
- regressions in API discovery, param.cgi fallback, or application handler
  initialization ordering.

4. Quality trigger:
- failure to satisfy lint/type/test release gates.

## Rollback Procedure

1. Revert runtime-removal commits from the feature branch.
2. Restore last green commit set with full test migration and green CI.
3. Re-run full validation matrix.
4. Publish incident note in PR with root-cause and adjusted rollout plan.

## Operational Notes

1. Keep `uv.lock` updates isolated from migration intent unless dependency inputs
   changed intentionally.
2. Preserve incremental commit discipline for any follow-up runtime changes.
3. Maintain PR checklist and commit ledger updates per increment.

## Phase 10 Exit Criteria

Phase 10 is complete when this sign-off is present in-repo and PR tracking marks
the final architecture sign-off and rollback gates as complete.