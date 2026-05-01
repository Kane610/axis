# Project Guidelines

## Build And Test

- Use the project environment managed by `uv` (see `README.md`).
- Preferred bootstrap: `./setup.sh`.
- Python requirement is `>=3.14.0` (see `pyproject.toml`).
- Standard full checks:
	- `uv run ruff check .`
	- `uv run ruff format --check .`
	- `uv run mypy axis`
	- `uv run pytest`
- After code changes, run targeted tests for touched files first; run broader validation when shared behavior is affected.

## Architecture

- Keep boundaries clear:
	- `axis/interfaces/` contains API handlers and transport-facing logic.
	- `axis/models/` contains request/response models, enums, and parsing helpers.
	- `axis/device.py` and `axis/interfaces/vapix.py` orchestrate device and handler lifecycle.
- Follow the phase-based handler initialization model documented in `README.md` (`API_DISCOVERY`, `PARAM_CGI_FALLBACK`, `APPLICATION`).
- Prefer boundary normalization for incoming values (for example, enum coercion and defaults in model constructors/post-init).

## Conventions

- Prefer minimal, targeted changes that preserve existing behavior unless the task explicitly requires a behavior change.
- Do not modify unrelated code, formatting, or tests.
- Never revert user changes unless explicitly asked.
- Before changing patterns or APIs, inspect nearby code and follow existing local style.
- Prefer root-cause fixes over workarounds.
- For enums and external inputs, preserve existing defensive normalization patterns (for example `_missing_` fallbacks and constructor normalization).
- For event/XML handling, preserve namespace-aware parsing and root-shape guards instead of assuming a fixed payload shape.

## Testing Conventions

- Add or update focused tests in the nearest relevant `tests/` module when behavior changes.
- Reuse existing async fixtures and HTTP mocking patterns from `tests/conftest.py`.
- If tests, typing, or linting fail for unrelated pre-existing reasons, report that clearly instead of fixing unrelated code.
- Expect commit hooks to run Ruff, Ruff format, and mypy; if hooks modify files, re-stage and re-run checks.

## Git Workflow

- Never create commits on the `master` branch.
- Never push commits directly to the `master` branch.
- Before any commit or push, check the current branch and confirm it is not `master`.
- If work is currently on `master`, create or switch to a feature branch before committing.
- If asked to commit or push from `master`, explain that the change must go through a feature branch and pull request.
- For any requested git operation, verify branch state first and summarize what will happen before committing or pushing.

## How to Ask Copilot for High-Quality Work

### Request Template

Use this template when asking Copilot to implement, fix, or refactor. Fill in each section to ensure clear scope and expectations:

```
[CONTEXT]
I'm working on [area: new handler / bug fix / test / refactor].
This touches [files/modules affected].
Related issue: [link or #number].

[CONSTRAINTS]
- Preserve existing behavior unless explicitly asked to change
- Follow the phase-based handler initialization model (see README.md)
- New code must have 100% test coverage
- Overall coverage must stay ≥95%
- Reuse fixtures from tests/conftest.py
- If enums are involved, include _missing_ fallback
- Keep changes minimal and targeted (no unrelated refactoring)

[TASK]
Please [implement / fix / refactor]:
1. [Specific step 1 with context]
2. [Specific step 2 with context]
3. [Specific step 3 with context]

[ACCEPTANCE CRITERIA]
- ✓ All checks pass: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy axis`, `uv run pytest`
- ✓ Tests added in `tests/test_<area>.py` covering new code (100% coverage)
- ✓ No unrelated changes
- ✓ Follows architectural layer boundaries (models vs. interfaces)

[VERIFICATION COMMAND]
uv run ruff check .
uv run ruff format --check .
uv run mypy axis
uv run pytest tests/test_<area>.py -v --cov=axis.<area> --cov-report=term-missing
```

### Tips

- **For new handlers:** Mention the API endpoint and expected response shape.
- **For bug fixes:** Paste the error trace and describe expected behavior.
- **For tests:** Link to the code under test and describe missing scenarios.
- **For reviews:** Use the Axis Review or Axis Review Verify agents instead (see below).

---

## How to Request Copilot Code Review

### Code Review Template

Use this when asking Copilot to review code for correctness and regressions. Choose the agent that matches your need:

#### Code Review Only (Axis Review Agent)

```
@axis-review: Please review my changes for correctness and regressions.

[CHANGED FILES]
- axis/interfaces/my_handler.py (new handler logic)
- tests/test_my_handler.py (new tests)

[FOCUS AREAS]
- Handler initialization phase behavior
- Enum normalization and _missing_ fallback handling
- XML parsing safety (namespace-aware, root-shape guards)
- Test coverage (100% for new code)
- Boundary respect (models vs. interfaces)

[KNOWN CONCERNS]
- Refactored the query builder (may have subtle regressions)
- Added new enum value (verify _missing_ handling)

[PASS CRITERIA]
- No behavior regressions
- All enums have _missing_ fallback
- Input boundary normalization present
- Tests cover changed code and error paths
```

#### Full Validation (Axis Review Verify Agent)

```
@axis-review-verify: Please validate my PR and run checks.

[CHANGED FILES]
- axis/interfaces/my_handler.py
- tests/test_my_handler.py

[RUN THESE CHECKS]
- uv run pytest tests/test_my_handler.py -v
- uv run ruff check axis/interfaces/my_handler.py
- uv run mypy axis

[REPORT EXPECTED]
- Code review findings (severity-ranked)
- Check results (pass/fail per command)
- Coverage impact
- Residual risks or gaps
```

#### When to Use Each Agent

| Task | Agent | Use When |
|---|---|---|
| Code review + risk analysis | Axis Review | After code is ready, before running tests |
| Code review + full test/lint/type validation | Axis Review Verify | Want comprehensive feedback and passing CI confidence |
| Both | Use Axis Review first, then Axis Review Verify | For thorough feedback with validation |

---

## Common Failure Modes & Anti-Patterns

### Enum Crashes on Unknown Device Values

**Anti-pattern:** Assuming enum always exists.

```python
# WRONG: Will crash if value is unknown
status = Status(user_input)

# RIGHT: Use _missing_ fallback
class Status(Enum):
    OK = "ok"
    ERROR = "error"
    UNKNOWN = "unknown"
    
    @classmethod
    def _missing_(cls, value: object) -> Status:
        LOGGER.debug("Unknown status: %s", value)
        return cls.UNKNOWN
```

**Why it matters:** Devices return unexpected values; unguarded enums crash at runtime.

### XML/Event Parsing Crashes on Unexpected Structure

**Anti-pattern:** Assuming fixed XML structure.

```python
# WRONG: Assumes 'event' root always exists
event_data = xmltodict.parse(payload)['event']

# RIGHT: Check root shape and use traverse helper
root = xmltodict.parse(payload, process_namespaces=True)
if root and 'event' in root:
    event_data = root['event']
else:
    LOGGER.warning("Unexpected XML structure")
    event_data = {}
```

**Why it matters:** Event streams vary by device firmware; fixed assumptions miss edge cases.

### Handler Initialization Phase Misuse

**Anti-pattern:** Handler initializes in wrong phase.

```python
# WRONG: Declares API_DISCOVERY but initializes in APPLICATION
class LightHandler(ApiHandler):
    handler_groups = {HandlerGroup.API_DISCOVERY}
    
    def should_initialize_in_group(self, group: HandlerGroup) -> bool:
        return group == HandlerGroup.APPLICATION  # Contradicts declaration
```

**Why it matters:** Phase-based ordering ensures dependencies are met; mismatches cause failures.

### Input Boundary Not Normalized

**Anti-pattern:** Not coercing enums at entry points.

```python
# WRONG: Device sends "http" but code expects HttpProtocol enum
class Config:
    def __init__(self, protocol: str):
        self.protocol = protocol

# RIGHT: Coerce at boundary
class Config:
    def __init__(self, protocol: str | HttpProtocol):
        self.protocol = HttpProtocol(protocol)
```

**Why it matters:** External inputs use strings; internal code expects enums. Normalizing at the boundary prevents type confusion.

### Incomplete Test Coverage

**Anti-pattern:** Testing only happy path.

```python
# WRONG: Only tests success
async def test_get_status():
    mock.respond(json={"status": "ok"})
    assert await handler.get_status() == "ok"

# RIGHT: Test success, error, and edge cases
async def test_get_status_success():
    mock.respond(json={"status": "ok"})
    assert await handler.get_status() == "ok"

async def test_get_status_unknown_value():
    mock.respond(json={"status": "unknown"})
    assert await handler.get_status() == StatusEnum.UNKNOWN

async def test_get_status_malformed():
    mock.respond(json={"data": []})  # Missing "status"
    with pytest.raises(KeyError):
        await handler.get_status()
```

**Why it matters:** Untested error paths ship bugs; coverage threshold catches them.

---

## Troubleshooting

### Coverage Dropped Below 95%

**Symptom:** CI fails with coverage check.

**Fix:**
1. Run `uv run pytest --cov=axis --cov-report=term-missing | grep axis/` to find gaps.
2. Add tests in `tests/test_<area>.py` for uncovered lines.
3. Ensure new code is 100% covered.
4. Rerun: `uv run pytest --cov=axis`.

---

### mypy Disallow Untyped Defs Error

**Symptom:** `error: Function is missing a return type annotation`.

**Fix:**
```python
# WRONG
async def get_status():
    return await self.device.api_call()

# RIGHT
async def get_status(self) -> str:
    return await self.device.api_call()
```

---

### Ruff Lint Errors

**Symptom:** `uv run ruff check .` reports errors.

**Fix:**
1. Run `uv run ruff check . --show-source` for details.
2. Use `uv run ruff check . --fix` to auto-fix simple issues.
3. For complex issues, read the rule documentation.

---

### Enum Crashes on Unknown Device Value

**Symptom:** `ValueError: 'unexpected_value' is not a valid <EnumName>`.

**Fix:** Implement `_missing_` (see Common Failure Modes above).

---

### XML Parsing KeyError

**Symptom:** `KeyError: 'event'` when parsing device response.

**Fix:** Check root shape before accessing (see Common Failure Modes above).

---

### Test Fixture Mismatch

**Symptom:** `TypeError: unsupported operand type` or fixture errors.

**Fix:**
1. Check [CONTRIBUTING.md](../../CONTRIBUTING.md) fixture table (aiohttp_mock_server vs. http_route_mock).
2. Ensure `async def test_*` (no decorator).
3. If overriding a fixture, document why in the fixture docstring.

---

### Pre-commit Hook Modifies Files

**Symptom:** After commit, files are modified by hooks.

**Fix:**
```bash
git add -u  # Stage the hook-modified files
git commit  # Re-commit
```