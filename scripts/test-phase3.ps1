# Test Phase 3 Prompt Intelligence Engine end-to-end
$ErrorActionPreference = "Stop"

$aiUrl = "http://localhost:8000"
$goUrl = "http://localhost:8080"

Write-Host "[Phase 3] Checking services..."

$aiHealth = Invoke-RestMethod -Uri "$aiUrl/api/v1/prompt/health" -Method Get
Write-Host "  AI prompt engine: $($aiHealth.status)"

$goHealth = Invoke-RestMethod -Uri "$goUrl/health" -Method Get
Write-Host "  Go server: $($goHealth.status)"

Write-Host "[Phase 3] Generating world..."
$world = Invoke-RestMethod -Uri "$goUrl/api/world/generate" -Method Post -ContentType "application/json" -Body (@{
    scenario_id = "scenario_1"
    scenario = "A fortress stands between a living forest and a restless ocean."
    seed = 42
    difficulty = 0.5
    world_size = 32.0
} | ConvertTo-Json)

$entities = @{}
foreach ($prop in $world.entities.PSObject.Properties) {
    $entities[$prop.Name] = @{ type = $prop.Value.type; name = $prop.Value.name }
}

Write-Host "[Phase 3] Interpreting prompt..."
$interpret = Invoke-RestMethod -Uri "$goUrl/api/prompt/interpret" -Method Post -ContentType "application/json" -Body (@{
    prompt = "The ocean rises and consumes the fortress."
    player_id = "human"
    turn = $world.turn
    world_id = $world.world_id
    world_context = @{ entities = $entities }
    history = @()
} | ConvertTo-Json -Depth 5)

Write-Host "  Status: $($interpret.status)"
Write-Host "  Action: $($interpret.action.action_type)"
Write-Host "  Confidence: $($interpret.confidence.overall_confidence)"
Write-Host "  Novelty: $($interpret.novelty)"

if ($interpret.status -ne "VALID") {
    Write-Host "[FAIL] Expected VALID status"
    exit 1
}

Write-Host "[Phase 3] Executing action..."
$execute = Invoke-RestMethod -Uri "$goUrl/api/prompt/execute" -Method Post -ContentType "application/json" -Body (@{
    prompt = "The ocean rises and consumes the fortress."
    actor = "human"
    action = $interpret.action
} | ConvertTo-Json -Depth 5)

Write-Host "  Transformer action: $($execute.parsed_action.action)"
Write-Host "  Affected: $($execute.transform.affected_ids -join ', ')"
Write-Host "[PASS] Phase 3 pipeline OK"
