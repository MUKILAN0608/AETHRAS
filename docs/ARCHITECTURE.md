# AETHRAS Architecture

## Overview

AETHRAS follows a **three-tier game architecture** where each layer has a single clear responsibility. Layers communicate via HTTP/JSON — never direct coupling between Godot and Python.

## Data Flow

```
Player
  ↓ (natural language prompt)
Godot Client
  ↓ POST /api/prompt
Go Game Server          ← authoritative orchestrator
  ↓ POST /api/parse
Python AI Service       ← inference / ML (mock parser in Phase 1)
  ↓ structured action JSON
Go Game Server          ← validates response shape
  ↓ JSON response
Godot Client
  ↓ apply visual effect
3D World State (rendering only)
```

## Layer Responsibilities

| Layer | Technology | Owns |
|-------|-----------|------|
| **Client** | Godot 4.x | 3D rendering, player input, HUD, visual effects, audio |
| **Game Server** | Go | Match state (future), turn management, action validation, WebSocket events (future), request orchestration |
| **AI Service** | Python FastAPI | Prompt parsing, LLM inference (future), embeddings, graph queries |
| **Infrastructure** | Docker | PostgreSQL (persistent game state), Redis (match cache) |

## Engineering Rules

1. **Modular architecture** — each service is independently deployable
2. **Go owns authoritative game state** — Godot is a thin client
3. **Python owns AI/ML inference** — no AI logic in Go or Godot
4. **No direct Godot ↔ Python** — all traffic through Go
5. **AI never directly modifies game state** — returns suggestions only
6. **Every AI output passes through a validator** (Go shape check now; full validator in Phase 2+)
7. **Never trust raw LLM output** — Pydantic schemas enforce structure
8. **Deterministic game logic separate from probabilistic AI** — Go/ Godot are deterministic; Python is probabilistic
9. **No unnecessary dependencies** — lightweight local dev first

## Phase 1 Components

### Godot (`game/godot/`)

- `scenes/main.tscn` — Camera, light, ground, player/AI markers, AI Core, 3 env objects, fortress
- `scripts/main.gd` — HTTP prompt submission to Go server
- `scripts/world_effects.gd` — FLOOD visual transformation (water plane, particles, lighting)

### Go Game Server (`server/game-server/`)

- `GET /health` — service health
- `POST /api/prompt` — receives prompt, forwards to Python, returns structured action

### Python AI Service (`ai/`)

- `GET /health` — service health
- `POST /api/parse` — **DEMO / PLACEHOLDER** mock semantic parser
- Pydantic schemas in `app/schemas.py`

### Infrastructure (`infrastructure/`)

- PostgreSQL 16 — game state persistence (prepared, not yet wired)
- Redis 7 — match state cache (prepared, not yet wired)

## Communication Protocol

### Prompt Request (Godot → Go)

```json
{
  "prompt": "The ocean rises and consumes the fortress."
}
```

### Parsed Action Response (Python → Go → Godot)

```json
{
  "intent": "environmental_action",
  "action": "FLOOD",
  "target": "FORTRESS",
  "confidence": 0.90,
  "demo": true
}
```

## Legacy Note

The `client/AethrasOdyssey/` Unity scaffold from a prior architecture phase is **not active**. The current prototype uses Godot as specified in the project research plan.
