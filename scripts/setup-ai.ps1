# Setup Python AI virtual environment and install dependencies
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$AiDir = Join-Path $Root "ai"
$VenvDir = Join-Path $AiDir ".venv"

Write-Host "Using Python 3.11 for ML package compatibility..." -ForegroundColor Cyan
$PythonExe = (py -3.11 -c "import sys; print(sys.executable)" 2>$null)
if (-not $PythonExe) {
    $PythonExe = (Get-Command python -ErrorAction Stop).Source
    Write-Warning "Python 3.11 not found, using: $PythonExe"
}

if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment at ai/.venv"
    & $PythonExe -m venv $VenvDir
}

$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
& $VenvPython -m pip install --upgrade pip

Write-Host "Installing PyTorch CPU build (no CUDA)..." -ForegroundColor Cyan
& $VenvPython -m pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu

Write-Host "Installing remaining dependencies..." -ForegroundColor Cyan
& $VenvPython -m pip install -r (Join-Path $AiDir "requirements.txt")

Write-Host "Recording exact package versions..." -ForegroundColor Cyan
& $VenvPython -m pip freeze | Out-File -Encoding utf8 (Join-Path $AiDir "requirements.lock.txt")

Write-Host "AI environment setup complete." -ForegroundColor Green
& $VenvPython -m pip list | Select-String "fastapi|torch|transformers|uvicorn"
