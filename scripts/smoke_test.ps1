param(
  [string]$BaseUrl = "http://127.0.0.1:8000"
)

$ErrorActionPreference = "Stop"

Write-Host "==> Smoke test start: $BaseUrl"

# 1) health check
try {
  $health = Invoke-RestMethod -Method Get -Uri "$BaseUrl/health" -TimeoutSec 10
  Write-Host "[OK] /health =>" ($health | ConvertTo-Json -Depth 5 -Compress)
} catch {
  Write-Host "[FAIL] /health request failed"
  Write-Host $_.Exception.Message
  exit 1
}

# 2) grade preview
$payload = @{
  text = "杩欐槸涓€娈电敤浜庡啋鐑熸祴璇曠殑鏂囨湰銆?
} | ConvertTo-Json -Depth 5

try {
  $resp = Invoke-RestMethod `
    -Method Post `
    -Uri "$BaseUrl/grade/preview" `
    -ContentType "application/json; charset=utf-8" `
    -Body $payload `
    -TimeoutSec 20

  $resp | ConvertTo-Json -Depth 10 | Out-File -FilePath "resp_utf8.json" -Encoding utf8
  Write-Host "[OK] /grade/preview => saved to resp_utf8.json"
} catch {
  Write-Host "[FAIL] /grade/preview request failed"

  if ($_.Exception.Response) {
    $sr = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    $errBody = $sr.ReadToEnd()
    Write-Host "HTTP Body:" $errBody
  } else {
    Write-Host $_.Exception.Message
  }
  exit 1
}

# 3) minimal contract check
if (-not $resp.template_id -or -not $resp.overall_score -or -not $resp.holistic_level -or -not $resp.analytic_scores) {
  Write-Host "[FAIL] response missing required fields"
  $resp | ConvertTo-Json -Depth 10
  exit 1
}

Write-Host "[PASS] smoke test passed"
exit 0
