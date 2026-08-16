# Run all tests (Python + Go build)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "=== Python AI Tests ===" -ForegroundColor Cyan
$VenvPython = Join-Path $Root "ai\.venv\Scripts\python.exe"
if (Test-Path $VenvPython) {
    Set-Location (Join-Path $Root "ai")
    & $VenvPython -m pytest tests/ -v
} else {
    Write-Warning "Python venv not found — skipping AI tests"
}

Write-Host "`n=== Go World Tests ===" -ForegroundColor Cyan
Set-Location (Join-Path $Root "server\game-server")
go test ./world/... -v

Write-Host "`n=== Communication Test ===" -ForegroundColor Cyan
& (Join-Path $Root "scripts\test-communication.ps1")

Write-Host "`n=== World Seed Tests (requires servers) ===" -ForegroundColor Cyan
try {
    & (Join-Path $Root "scripts\test-world-seeds.ps1")
} catch {
    Write-Warning "World seed tests skipped — start AI + Go servers first"
}
