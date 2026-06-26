# Changelog

## v0.1.3 (Unreleased)

### Added
- TBD

### Changed
- TBD

### Fixed
- TBD

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
