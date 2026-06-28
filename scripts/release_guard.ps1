param(
  [Parameter(Mandatory = $true)]
  [string]$Tag
)

$ErrorActionPreference = "Stop"

git fetch origin master --tags | Out-Null

$tagExists = git rev-parse -q --verify "refs/tags/$Tag" 2>$null
if ($LASTEXITCODE -eq 0) {
  Write-Host "[FAIL] tag '$Tag' already exists"
  exit 1
}

$headSha = (git rev-parse HEAD).Trim()
$masterSha = (git rev-parse origin/master).Trim()

if ($headSha -ne $masterSha) {
  Write-Host "[FAIL] HEAD ($headSha) is not origin/master ($masterSha)"
  Write-Host "       Please merge PR and fast-forward master first."
  exit 1
}

Write-Host "[OK] release guard passed on $headSha"
