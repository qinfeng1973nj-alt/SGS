# Changelog

All notable changes to this project are documented in this file.  
The format follows a Keep a Changelog–style structure and Semantic Versioning in practice.

## v0.2.7 - Trace Cleanup

- 标准化 Trace ID 解析优先级：`X-Trace-Id > X-Request-ID > UUID`
- 响应头统一输出 `X-Trace-Id`，并保留 `X-Request-ID` 兼容旧客户端
- 同步最终 trace 到 `request.state.request_id`
- 保证错误信封 `error.trace_id` 与响应头 `X-Trace-Id` 严格一致（含 404）
- 新增/完善相关测试与文档，确保行为可回归验证

## v0.2.1 - 2026-06-29

### Added
- Added `GET /healthz` liveness endpoint.
- Added `GET /version` endpoint exposing build metadata from `APP_VERSION` and `GIT_SHA`.

### Changed
- Unified API error response envelope to include:
  - `code`
  - `reason`
  - `message`
  - `path`
  - `trace_id`
- Improved request traceability via `request.state.request_id`.

### Fixed
- Mapped malformed JSON on `/score` to `INVALID_TYPE` while preserving compatibility semantics for existing validation flows.

### Verification
- Full test suite passed: `pytest -q` (21 passed).

---

## v0.1.9 - 2026-06-28

### Notes
- Patch release tag reserved in history; no additional functional changes documented in changelog.

---

## v0.1.8 - 2026-06-28
### Added
- Added `scripts/release_guard.ps1` to enforce pre-release checks (tag base must be on `origin/master`).

### Verification
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\release_guard.ps1 -Tag v0.1.8-rc
```
```text
[OK] release guard passed on 0d58cd4fa6bca44f49354bacbe049e77272e39be
```

## v0.1.7 - 2026-06-27
### Notes
- Historical version tag exists; detailed release notes were not recorded at the time.

## v0.1.6 - 2026-06-27
### Notes
- Historical version tag exists; detailed release notes were not recorded at the time.

## v0.1.5 - 2026-06-27
### Notes
- Historical version tag exists; detailed release notes were not recorded at the time.

## v0.1.4 - 2026-06-26
### Notes
- Historical version tag exists; detailed release notes were not recorded at the time.

## v0.1.3 - 2026-06-26
### Fixed
- Stabilized LLM-path unit tests by mocking external calls (no real API dependency in CI).
- Aligned over-limit text test with current `/score` behavior.
- Added boundary cases for text length and null input handling.

### Changed
- Restrict pytest discovery scope to `tests/` via `pytest.ini` to avoid accidental collection.
- Harden smoke-test reliability and ensure deterministic test execution across environments.

## v0.1.2 - 2026-06-26
### Changed
- Finalized README formatting and contract verification section
- Enforced `student_text` boundary validation (`min_length=20`, `max_length=20000`)
- Added/verified boundary tests and smoke-test workflow

## v0.1.1 - 2026-06-25
### Added
- Freeze scorer contract (`docs/score_contract.md`)
- Add smoke test script (`scripts/smoke_test.ps1`)
### Changed
- Align CI workflow and app behavior (`.github/workflows/smoke.yml`, `app/main.py`)
- Update README and UTF-8 response sample (`README.md`, `resp_utf8.json`)

## v0.1.0 - 2026-06-21
### Added
- Initial score endpoint with pydantic schemas
- Endpoint validated via `/docs`

