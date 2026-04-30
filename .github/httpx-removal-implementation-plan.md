# Runtime HTTPX Removal Implementation Plan

## Scope

This plan defines how runtime support for `httpx` will be removed while preserving
existing behavior for Axis request handling, auth fallback, and error semantics.

The test migration has already moved request/response test behavior to
`aiohttp_server`-backed flows. Remaining Phase 8 work is runtime-only.

## Current Runtime Coupling (Inventory)

1. `axis/interfaces/vapix.py`
- Imports `httpx` and supports two request engines (`httpx` and `aiohttp`).
- Constructs `httpx.BasicAuth` and `httpx.DigestAuth` for non-`aiohttp` sessions.
- Routes requests through `_perform_httpx_request` when session is not `aiohttp`.
- Maps `httpx.TimeoutException`, `httpx.TransportError`, and
  `httpx.RequestError` to `RequestError`.
- Uses `httpx.DigestAuth` type checks for AUTO fallback behavior.

2. `axis/models/configuration.py`
- `Configuration.session` is typed as `AsyncClient | ClientSession`.
- Type-checking import references `httpx.AsyncClient`.

3. `pyproject.toml`
- Runtime dependency list includes `httpx>=0.26`.
- Optional pinned requirements include `httpx==0.28.1`.

4. Tests
- `tests/test_configuration.py` still validates `httpx.AsyncClient` acceptance in
  `Configuration`.
- `tests/test_vapix.py` and `tests/respx_shim.py` reference `httpx` exceptions to
  assert request-error translation behavior.
- `tests/test_http_client_compat.py` already validates `aiohttp` runtime behavior.

## Target Runtime Contract

1. Runtime session type is `aiohttp.ClientSession` only.
2. Runtime auth types are `aiohttp.BasicAuth` or digest handled by
   `AiohttpDigestAuth` / `DigestAuthMiddleware` when available.
3. Request execution path is single-engine (`aiohttp`) only.
4. Public behavior remains unchanged:
- same `RequestError` mapping for timeout/connection/general request failures,
- same status-code-to-Axis-error mapping,
- same AUTO auth fallback semantics.

## Ordered Execution Plan

1. Narrow configuration typing to `aiohttp.ClientSession`
- Update `axis/models/configuration.py` to remove `httpx.AsyncClient` references
  and define `HTTPSession = ClientSession`.
- Update tests that currently expect mixed-session acceptance.

2. Remove dual-engine request logic from `Vapix`
- Delete `_perform_httpx_request`, `_httpx_session`, `_httpx_auth`, and
  `_client_name` branching.
- Remove `httpx.BasicAuth`/`httpx.DigestAuth` construction paths.
- Keep `_perform_aiohttp_request` as the single request engine.

3. Preserve exception mapping semantics without `httpx`
- Replace explicit `httpx` exception branches with `aiohttp` and generic timeout
  handling while preserving current `RequestError` messages:
  - timeout -> `RequestError("Timeout")`
  - connection issues -> `RequestError("Connection error: ...")`
  - other client errors -> `RequestError("Unknown error: ...")`

4. Adjust AUTO auth fallback checks
- Replace `httpx.DigestAuth`-specific checks in `_should_retry_with_basic` with
  client-agnostic state checks that still enforce one retry.

5. Update dependency metadata
- Remove `httpx` from runtime dependencies in `pyproject.toml`.
- Remove pinned `httpx` entry from `project.optional-dependencies.requirements`.

6. Update tests to reflect aiohttp-only runtime
- Replace or remove tests that assert `httpx.AsyncClient` compatibility in
  `tests/test_configuration.py`.
- Keep and extend `tests/test_http_client_compat.py` for auth and request parity.
- Update `tests/test_vapix.py` and `tests/respx_shim.py` to avoid direct `httpx`
  exception dependencies while preserving equivalent behavior assertions.

7. Validation gates
- `uv run ruff check axis tests`
- `uv run ruff format --check axis tests`
- `uv run mypy axis`
- targeted pytest for touched suites first
- `uv run pytest`

## Risks And Mitigations

1. Risk: subtle auth regression in AUTO mode.
- Mitigation: retain and expand fallback tests around `WWW-Authenticate` handling.

2. Risk: changed exception text breaks downstream consumers/tests.
- Mitigation: preserve existing `RequestError` message strings verbatim.

3. Risk: digest middleware availability differs by aiohttp version.
- Mitigation: keep current middleware availability guard and digest helper fallback.

## Exit Criteria

Phase 8 is complete when all are true:

1. Runtime package no longer depends on `httpx`.
2. Production code under `axis/` has no `import httpx` references.
3. `Configuration` and `Vapix` are aiohttp-only at runtime.
4. Existing request/auth/error behavior is preserved by tests.
5. Full lint/type/test matrix passes.