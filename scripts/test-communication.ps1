# End-to-end communication test: Go -> Python -> World Transform
$ErrorActionPreference = "Stop"

$AiHealth = "http://localhost:8000/health"
$GoHealth = "http://localhost:8080/health"
$GoGenerate = "http://localhost:8080/api/world/generate"
$GoPrompt = "http://localhost:8080/api/prompt"

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Body = $null
    )
    try {
        if ($Method -eq "GET") {
            $r = Invoke-RestMethod -Uri $Url -TimeoutSec 5
        } else {
            $json = $Body | ConvertTo-Json -Depth 6
            $r = Invoke-RestMethod -Uri $Url -Method POST -Body $json -ContentType "application/json" -TimeoutSec 10
        }
        Write-Host "[PASS] $Name" -ForegroundColor Green
        return $r
    } catch {
        Write-Host "[FAIL] $Name" -ForegroundColor Red
        Write-Host $_.Exception.Message
        return $null
    }
}

Write-Host "=== AETHRAS Communication Test (Phase 2) ===" -ForegroundColor Cyan

Test-Endpoint -Name "Python /health" -Url $AiHealth
Test-Endpoint -Name "Go /health" -Url $GoHealth

$genBody = @{
    scenario_id = "scenario_1"
    scenario    = "A fortress stands between a living forest and a restless ocean."
    seed        = 42
    difficulty  = 0.5
    world_size  = 32.0
}
$world = Test-Endpoint -Name "World generation" -Url $GoGenerate -Method "POST" -Body $genBody

if ($null -ne $world -and $null -ne $world.entities) {
    $count = ($world.entities.PSObject.Properties | Measure-Object).Count
    Write-Host "[INFO] Generated world with $count entities" -ForegroundColor Cyan
}

$promptBody = @{ prompt = "The ocean rises."; actor = "human" }
$result = Test-Endpoint -Name "Go Python World Transform" -Url $GoPrompt -Method "POST" -Body $promptBody

if ($null -ne $result) {
    $action = $result.parsed_action.action
    $target = $result.parsed_action.target
    $turn = $result.transform.world_state.turn
    if ($action -eq "FLOOD") {
        Write-Host "[PASS] Pipeline FLOOD target $target turn $turn" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Unexpected action $action target $target" -ForegroundColor Yellow
    }
}
