# Start Docker infrastructure (PostgreSQL + Redis)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$InfraDir = Join-Path $Root "infrastructure"
$EnvFile = Join-Path $Root ".env"

if (-not (Test-Path $EnvFile)) {
    Write-Host "No .env found - copying from .env.example"
    Copy-Item -Path (Join-Path $Root ".env.example") -Destination $EnvFile
}

Set-Location $InfraDir
docker compose --env-file $EnvFile up -d
docker compose ps
