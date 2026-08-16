# Start Go game server
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$ServerDir = Join-Path $Root "server\game-server"

Set-Location $ServerDir

if (-not (Test-Path (Join-Path $ServerDir "go.sum"))) {
    go mod tidy
}

go run .
