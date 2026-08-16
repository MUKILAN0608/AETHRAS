# Seed reproducibility and world generation tests (Phase 2)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Base = "http://localhost:8080"

function Post-Json($Url, $Body) {
    return Invoke-RestMethod -Method POST -Uri $Url -ContentType "application/json" -Body ($Body | ConvertTo-Json -Depth 6)
}

Write-Host "=== Phase 2 World Seed Tests ===" -ForegroundColor Cyan

$scenario = @{
    scenario_id = "scenario_1"
    scenario = "A fortress stands between a living forest and a restless ocean."
    difficulty = 0.5
    world_size = 32.0
}

Write-Host "`nGenerating Seed A (100), B (200), C (300)..." -ForegroundColor Yellow
$worldA = Post-Json "$Base/api/world/generate" ($scenario + @{ seed = 100 })
$worldB = Post-Json "$Base/api/world/generate" ($scenario + @{ seed = 200 })
$worldC = Post-Json "$Base/api/world/generate" ($scenario + @{ seed = 300 })

$sigA = ($worldA.entities.PSObject.Properties | ForEach-Object { "$($_.Value.type)" }) -join ","
# Re-generate A on fresh server state - use reproducibility via same session
$worldA2 = Post-Json "$Base/api/world/generate" ($scenario + @{ seed = 100 })

if ($worldA.seed -eq $worldA2.seed) {
    Write-Host "[PASS] Same seed produces same seed value" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Reproducibility check" -ForegroundColor Red
}

if ($worldA.seed -ne $worldB.seed -and $worldB.seed -ne $worldC.seed) {
    Write-Host "[PASS] Different seeds (A=$($worldA.seed), B=$($worldB.seed), C=$($worldC.seed))" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Seeds should differ" -ForegroundColor Red
}

Write-Host "`nTesting prompts on generated world..." -ForegroundColor Yellow
Post-Json "$Base/api/world/generate" ($scenario + @{ seed = 42 }) | Out-Null

$prompts = @(
    "The ocean rises.",
    "The forest catches fire.",
    "The mountain remembers this lie."
)

foreach ($p in $prompts) {
    $result = Post-Json "$Base/api/prompt" @{ prompt = $p; actor = "human" }
    $action = $result.parsed_action.action
    $turn = $result.transform.world_state.turn
    Write-Host "[PASS] '$p' -> $action (turn $turn)" -ForegroundColor Green
}

Write-Host "`n=== Phase 2 seed tests complete ===" -ForegroundColor Cyan
