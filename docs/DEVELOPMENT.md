# AETHRAS Development Guide

## Environment Setup

### 1. Machine Requirements

- Windows 10/11 (primary dev platform)
- 8 GB+ RAM (16 GB recommended)
- Docker Desktop for infrastructure services
- No CUDA required for Phase 1 (CPU-only PyTorch)

### 2. Initial Setup

```powershell
# Clone and enter repo
cd Propmt_game

# Environment variables
Copy-Item .env.example .env
# Edit .env — change POSTGRES_PASSWORD and REDIS_PASSWORD

# Python AI environment
.\scripts\setup-ai.ps1

# Docker infrastructure
.\scripts\start-infrastructure.ps1
```

### 3. Daily Development

Open **three terminals**:

```powershell
# Terminal 1 — AI service
.\scripts\start-ai.ps1

# Terminal 2 — Go game server
.\scripts\start-game-server.ps1

# Terminal 3 — Godot
.\scripts\launch-godot.ps1
```

Press **F5** in Godot to run the scene.

## Service Ports

| Service | Port | Health URL |
|---------|------|------------|
| Python AI | 8000 | http://localhost:8000/health |
| Go Server | 8080 | http://localhost:8080/health |
| PostgreSQL | 5432 | via `docker compose ps` |
| Redis | 6379 | via `docker compose ps` |

## Running Tests

```powershell
# All tests + communication pipeline
.\scripts\run-tests.ps1

# Python only
cd ai
.\.venv\Scripts\python.exe -m pytest tests/ -v

# Go build only
cd server\game-server
go build .
```

## Manual API Testing

```powershell
# Python health
Invoke-RestMethod http://localhost:8000/health

# Go health
Invoke-RestMethod http://localhost:8080/health

# Full pipeline
Invoke-RestMethod -Method POST -Uri http://localhost:8080/api/prompt `
  -ContentType "application/json" `
  -Body '{"prompt":"The ocean rises and consumes the fortress."}'
```

## Adding Dependencies

### Python

1. Add to `ai/requirements.txt` with pinned version
2. `.\scripts\setup-ai.ps1` (or pip install manually)
3. Update `ai/requirements.lock.txt`

**Rule:** Do not add packages unless genuinely needed. Do not download model weights during setup.

### Go

```powershell
cd server\game-server
go get package@version
go mod tidy
```

## Godot Development Notes

- Project path: `game/godot/`
- Main scene: `scenes/main.tscn`
- Server URL: `scripts/game_config.gd` → `GAME_SERVER_URL`
- All scripts use GDScript with typed variables (Godot 4.x)

## Docker Management

```powershell
cd infrastructure
docker compose --env-file ..\.env up -d      # start
docker compose --env-file ..\.env down       # stop
docker compose --env-file ..\.env logs -f      # logs
docker compose --env-file ..\.env ps           # status
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Godot HTTP fails | Ensure Go server is running on port 8080 |
| Go returns 502 | Ensure Python AI is running on port 8000 |
| torch install fails | Use Python 3.11: `py -3.11 -m venv ai/.venv` |
| Docker port conflict | Change ports in `.env` |
| Godot not found | `winget install GodotEngine.GodotEngine` |

## Code Standards

- Python: type hints, Pydantic schemas, async endpoints
- Go: standard library first, explicit error handling
- GDScript: typed variables, signals for UI events
- All AI responses marked `demo: true` until Phase 3
