# AETHRAS — Where Words Become Worlds

AETHRAS is a playable human-vs-AI strategic game where **natural-language prompts are the player's primary weapon**. The player writes statements like *"The ocean rises and consumes the fortress."* — the system interprets them as structured game actions, modifies a dynamic 3D world, and allows the AI to reason about and counter the changed state.

## Current Status

**Phase 3 — Prompt Intelligence Engine** (complete)

- Multi-stage pipeline: Normalize → Intent → Entities → Strategy → Compile → Critic → Validate
- Python `/api/v1/prompt/interpret`, `/validate`, `/compile`, `/health`
- Go interpret + execute endpoints with Phase 3 → Phase 2 action mapping
- Godot two-step flow: **Interpret Prompt** → review → **Execute**
- Research logging to `ai/app/logs/experiments.jsonl`
- 28 Python tests + Go world tests passing

See [docs/PHASE3_PROMPT_ENGINE.md](docs/PHASE3_PROMPT_ENGINE.md).

**Phase 2 — Dynamic Semantic World Engine** (complete)

- Procedurally generated 3D worlds from scenario + seed (no fixed map)
- Go authoritative world state with transformer, events, history, snapshots
- Godot renderer with terrain, entities, environment FX, dynamic camera
- Legacy mock parser at `/api/parse` retained for compatibility

See [docs/PHASE2_WORLD_ENGINE.md](docs/PHASE2_WORLD_ENGINE.md).

## Architecture

```
Player → Godot (rendering + input)
           ↓ HTTP
         Go Game Server (authoritative orchestration)
           ↓ HTTP
         Python AI Service (inference / parsing)
           ↓
         Structured Action → Go → Godot → Visual Consequence
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for full details.

## Prerequisites

| Tool | Version (tested) |
|------|------------------|
| Godot | 4.7.1 |
| Python | 3.11+ (3.11 recommended for torch) |
| Go | 1.23+ |
| Docker | 29.x |
| Docker Compose | 5.x |

## Installation

```powershell
# 1. Copy environment variables
Copy-Item .env.example .env

# 2. Setup Python AI virtual environment
.\scripts\setup-ai.ps1

# 3. Start infrastructure (PostgreSQL + Redis)
.\scripts\start-infrastructure.ps1
```

## Development Commands (Windows PowerShell)

```powershell
# Start Python AI service (port 8000)
.\scripts\start-ai.ps1

# Start Go game server (port 8080) — in a separate terminal
.\scripts\start-game-server.ps1

# Launch Godot editor
.\scripts\launch-godot.ps1

# Run all tests + communication check
.\scripts\run-tests.ps1

# Test Go → Python pipeline only
.\scripts\test-communication.ps1
```

### Linux/macOS equivalents

```bash
cd ai && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
cd server/game-server && go run .
cd infrastructure && docker compose --env-file ../.env up -d
godot --path game/godot
```

## Testing the Demo

1. Start AI service and Go server (two terminals)
2. Launch Godot and press **Play**
3. Click **Generate World**, then use the default prompt: *"The ocean rises and consumes the fortress."*
4. Click **Interpret Prompt** — UI shows intent, entities, strategy, confidence, novelty, status
5. Click **Execute** — world visibly changes (flood effect on fortress)
6. Or run integration test: `.\scripts\test-phase3.ps1`

## Future AI Architecture

Long-term modules (not yet implemented):

- Prompt Engineering, Real LLM integration, Mixture-of-Experts
- Liquid Neural Networks, Theory-of-Mind, World Models
- Spatial AI, Self-Evolving AI, Semantic memory
- Formal contradiction detection, Test-time strategic search
- Optional quantum-inspired reasoning, Human-AI co-adaptation

See [docs/ROADMAP.md](docs/ROADMAP.md).

## Known Limitations

- **MockLLM pipeline** — deterministic rule-based inference, not a real LLM yet
- **No model weights downloaded** — torch/transformers installed but unused
- **No match state** — Go server forwards prompts only; PostgreSQL/Redis not wired yet
- **Intel integrated GPU** — CPU-only PyTorch; no CUDA
- **Legacy Unity scaffold** — `client/` folder from prior architecture phase (inactive)

## Project Structure

```
AETHRAS/
├── game/godot/           Godot 4 project
├── ai/                   Python FastAPI AI service
├── server/game-server/   Go authoritative game server
├── infrastructure/       Docker Compose (PostgreSQL, Redis)
├── docs/                 Architecture, development, roadmap
├── scripts/              PowerShell dev scripts
├── client/               (Legacy Unity scaffold — not active)
└── .env.example
```

## License

See [LICENSE](LICENSE).
