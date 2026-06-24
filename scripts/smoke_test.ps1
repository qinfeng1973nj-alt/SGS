param(
  [string]$BaseUrl = "http://127.0.0.1:8000"
)

$ErrorActionPreference = "Stop"

Write-Host "[INFO] BaseUrl = $BaseUrl"

# 1) health
try {
  $health = Invoke-RestMethod -Method Get -Uri "$BaseUrl/health"
  if (-not $health.ok) {
    Write-Host "[FAIL] /health ok != true"
    exit 1
  }
  Write-Host "[PASS] /health"
}
catch {
  Write-Host "[FAIL] /health request failed"
  Write-Host $_
  exit 1
}

# 2) grade preview
$payloadObj = @{
  student_text = "Alice 的成绩是：语文95，数学88，英语92。请给出等级预览。"
}
$payload = $payloadObj | ConvertTo-Json -Depth 5

try {
  $resp = Invoke-RestMethod -Method Post `
    -Uri "$BaseUrl/grade/preview" `
    -ContentType "application/json" `
    -Body $payload

  if ($null -eq $resp) {
    Write-Host "[FAIL] /grade/preview empty response"
    exit 1
  }

  # 若你的接口不是 grade 字段，这里改成真实字段名
  if ($resp.PSObject.Properties.Name -notcontains "holistic_level") {
  Write-Host "[FAIL] /grade/preview missing field: holistic_level"
  $resp | ConvertTo-Json -Depth 10
  exit 1
}


  $resp | ConvertTo-Json -Depth 10 | Out-File -FilePath ".\resp_utf8.json" -Encoding utf8
  Write-Host "[PASS] /grade/preview"
}
catch {
  Write-Host "[FAIL] /grade/preview request failed"
  Write-Host $_
  exit 1
}

Write-Host "[PASS] smoke test passed"
exit 0
