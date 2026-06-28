# CHANGELOG

## v0.1.8 - 2026-06-28

### Added
- Add `scripts/release_guard.ps1` to enforce pre-release checks for tag base on `origin/master`.

### Validation
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\release_guard.ps1 -Tag v0.1.8-rc
```
```text
[OK] release guard passed on 0d58cd4fa6bca44f49354bacbe049e77272e39be
```

## v0.1.3 - 2026-06-26

### Fixed
- Stabilize LLM-path unit tests by mocking external calls (no real API dependency in CI).
- Align over-limit text test with current `/score` behavior.
- Add boundary cases for text length and null input handling.

### CI
- Restrict pytest discovery scope to `tests/` via `pytest.ini` to avoid accidental collection.
- Harden smoke-test reliability and ensure deterministic test execution across environments.

## v0.1.2 - 2026-06-26
- Finalized README formatting and contract verification section
- Enforced `student_text` boundary validation (`min_length=20`, `max_length=20000`)
- Added/verified boundary tests and smoke-test workflow

## v0.1.1 - 2026-06-25
- Freeze scorer contract (`docs/score_contract.md`)
- Add smoke test script (`scripts/smoke_test.ps1`)
- Align CI workflow and app behavior (`.github/workflows/smoke.yml`, `app/main.py`)
- Update README and UTF-8 response sample (`README.md`, `resp_utf8.json`)

## v0.1.0 - 2026-06-21
- Initial score endpoint with pydantic schemas
- Endpoint validated via `/docs`

