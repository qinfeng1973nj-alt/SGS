param(
  [int]$Port = 8001
)

$ErrorActionPreference = "Stop"
$base = "http://127.0.0.1:$Port"
$outFile = Join-Path $PSScriptRoot "..\resp_utf8.json"

function Write-Section($msg) {
  Write-Host ""
  Write-Host "==> $msg" -ForegroundColor Cyan
}

try {
  Write-Section "Checking /health"
  $h = Invoke-RestMethod -Uri "$base/health" -TimeoutSec 5
  Write-Host "[PASS] Health OK: $($h | ConvertTo-Json -Compress)" -ForegroundColor Green

  Write-Section "Checking /grade/preview"
  $bodyObj = @{
    student_text = "患者男性，45岁。3天前受凉后出现发热、咳嗽、咳黄痰，体温最高38.6℃，伴乏力，无胸痛，无咯血。既往有高血压病史5年，规律服药。"
  }
  $bodyJson = $bodyObj | ConvertTo-Json -Depth 5

  $p = Invoke-RestMethod -Uri "$base/grade/preview" `
    -Method POST `
    -ContentType "application/json; charset=utf-8" `
    -Body $bodyJson `
    -TimeoutSec 20

  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($outFile, ($p | ConvertTo-Json -Depth 15), $utf8NoBom)

  Write-Host "[PASS] Preview OK" -ForegroundColor Green
  Write-Host "[INFO] Output: $(Resolve-Path $outFile)" -ForegroundColor Yellow
  Write-Host ("[INFO] template_id={0}, overall_score={1}, holistic_level={2}" -f $p.template_id, $p.overall_score, $p.holistic_level) -ForegroundColor Gray

  exit 0
}
catch {
  Write-Host ""
  Write-Host "[ERROR] Smoke test failed." -ForegroundColor Red
  Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red

  try {
    $resp = $_.Exception.Response
    if ($null -ne $resp) {
      $statusCode = [int]$resp.StatusCode
      Write-Host "[ERROR] HTTP Status: $statusCode" -ForegroundColor Red

      $stream = $resp.GetResponseStream()
      if ($null -ne $stream) {
        $reader = New-Object System.IO.StreamReader($stream)
        $respBody = $reader.ReadToEnd()
        if (-not [string]::IsNullOrWhiteSpace($respBody)) {
          Write-Host "[ERROR] Response Body: $respBody" -ForegroundColor DarkRed
        }
      }
    }
  }
  catch {
    Write-Host "[WARN] Failed to parse error response body." -ForegroundColor Yellow
  }

  exit 1
}
