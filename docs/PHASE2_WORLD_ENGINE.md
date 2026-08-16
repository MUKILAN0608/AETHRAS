# Phase 2: Dynamic Semantic World Engine

## Overview

Phase 2 implements the **Dynamic Semantic World Engine** — procedurally generated, state-driven worlds that evolve through player prompts. There is **no fixed map**.

## Architecture

```
Natural Language (Godot UI)
        ↓
Go Game Server (authoritative WorldState)
        ↓ POST /api/parse
Python AI Service (mock parser — DEMO)
        ↓ structured action
Go Action Validator + WorldTransformer
        ↓ incremental state update
Godot WorldRenderer (visualization only)
```

**Rule:** Language never directly controls graphics. All changes flow through structured actions → deterministic simulation → renderer.

## World Engine Components

### Go Server (`server/game-server/world/`)

| File | Responsibility |
|------|----------------|
| `state.go` | Canonical WorldState, Entity, Relation, Region |
| `generator.go` | Procedural world from scenario + seed |
| `transformer.go` | Deterministic action → state changes |
| `rules.go` | Action validation |
| `events.go` | Causal event processor |
| `simulation.go` | Environmental tick (weather, fire, water) |
| `manager.go` | Session manager + snapshots |

### Godot Client (`game/godot/world/`)

| File | Responsibility |
|------|----------------|
| `world_state.gd` | Parse server JSON into typed state |
| `world_entity.gd` | Entity data class |
| `world_relation.gd` | Relationship data class |
| `world_event.gd` | Event data class |
| `semantic_world.gd` | HTTP orchestration |
| `world_renderer.gd` | State → visuals coordinator |
| `entity_renderer.gd` | Incremental entity mesh updates |
| `environment_renderer.gd` | Water, fire, storm, lighting |
| `world_generator.gd` | Procedural terrain mesh |
| `dynamic_camera.gd` | Event-responsive camera |
| `world_transformer.gd` | Display helper (logic on Go) |
| `world_rules.gd` | Color/type mapping |
| `event_processor.gd` | Visual event queue |

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/scenarios` | List 3 test scenarios |
| POST | `/api/world/generate` | Generate world from scenario + seed |
| GET | `/api/world/state` | Current world state |
| GET/POST | `/api/world/tick` | Advance environmental simulation |
| GET | `/api/world/history` | World memory / history |
| GET | `/api/world/snapshots` | Turn snapshots for replay |
| POST | `/api/prompt` | Parse + transform + return state |

## Test Scenarios

1. *"A fortress stands between a living forest and a restless ocean."*
2. *"A ruined city floats above a world of endless storms."*
3. *"A civilization survives around a mountain that changes shape whenever someone lies."*

## Test Prompts

| Prompt | Action | Expected Effect |
|--------|--------|-----------------|
| "The ocean rises." | FLOOD | Water level ↑, nearby entities flooded |
| "The forest catches fire." | FIRE | Forest burns, smoke, spread cascade |
| "The mountain remembers this lie." | MEMORY_REMEMBER | Mountain shape shift, memory relation |

## Seed Reproducibility

```powershell
.\scripts\test-world-seeds.ps1
```

Same scenario + same seed → reproducible initial world.  
Different seeds → different entity layouts.

## Running Phase 2 Demo

```powershell
.\scripts\start-ai.ps1          # Terminal 1
.\scripts\start-game-server.ps1 # Terminal 2
.\scripts\launch-godot.ps1      # Terminal 3
```

1. Select scenario + seed → **Generate World**
2. Enter prompt → **Submit Prompt**
3. **Advance Environment (Tick)** for weather/fire/water simulation
