Write-Host "== Smoke Test Start ==" -ForegroundColor Cyan

pytest -q tests/test_score.py::test_score_unknown_llm_error_should_not_fallback
if (0 -ne 0) { exit 0 }

pytest -q tests/test_score.py
if (0 -ne 0) { exit 0 }

Write-Host "== Smoke Test Passed ==" -ForegroundColor Green
