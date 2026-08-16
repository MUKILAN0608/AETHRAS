# Prompt Intelligence Engine — Phase 3

Natural language prompts flow through a multi-stage pipeline before any world change occurs.

## Pipeline

```
Prompt → Normalize → Intent/Entities/Relations/Temporal
      → Strategic Analysis → Constraints → Compile → Critic → Validate
```

## API Endpoints (Python `:8000`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/prompt/interpret` | Full pipeline |
| POST | `/api/v1/prompt/validate` | Validate action proposal |
| POST | `/api/v1/prompt/compile` | Compile interpretation only |
| GET | `/api/v1/prompt/health` | Engine health |
| POST | `/api/parse` | Legacy Phase 2 parser |

## Go Server Endpoints (`:8080`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/prompt/interpret` | Forward to Python interpret |
| POST | `/api/prompt/execute` | Apply validated action to world |
| POST | `/api/prompt` | Legacy direct parse+execute |

## Godot Flow

1. **Interpret Prompt** — async `POST /api/prompt/interpret`
2. UI shows intent, entities, strategy, confidence, novelty, status
3. **Execute** — async `POST /api/prompt/execute` (only when not INVALID)

## Action Mapping (Phase 3 → Phase 2)

| Phase 3 | Phase 2 Transformer |
|---------|---------------------|
| RAISE_WATER | FLOOD |
| START_FIRE | FIRE |
| MEMORY_ADD | MEMORY_REMEMBER |
| CREATE_STORM / SPATIAL_BYPASS | STORM |
| INDIRECT_STRUCTURAL_ATTACK | TRANSFORM |

## Tests

```powershell
cd ai
.\.venv\Scripts\Activate.ps1
pytest tests/ -v
```

## Research Logging

Experiment records append to `ai/app/logs/experiments.jsonl`.
