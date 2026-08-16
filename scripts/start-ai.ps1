# Start Python AI service (FastAPI + uvicorn)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$AiDir = Join-Path $Root "ai"
$VenvPython = Join-Path $AiDir ".venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Error "Virtual environment not found. Run scripts/setup-ai.ps1 first."
}

Set-Location $AiDir
& $VenvPython -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
