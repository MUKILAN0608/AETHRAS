# Complete Folder Hierarchy

Every folder exists to enforce separation of concerns, enable parallel development, and support research reproducibility.

---

## Repository Root

```
AETHRAS/                              # Monorepo root (Propmt_game)
├── client/                           # Unity 6 LTS project — all game runtime code & assets
├── server/                           # Python FastAPI — AI narrative backend (decoupled)
├── docs/                             # Architecture, API, research, ADRs
├── tools/                            # Build scripts, CI helpers, automation
├── .github/                          # GitHub Actions, issue/PR templates
├── .gitignore
├── LICENSE
└── README.md
```

**Why monorepo:** Single source of truth for client/server API contracts; atomic commits across Unity + backend.

---

## Unity Client

```
client/AethrasOdyssey/
├── Assets/
│   └── _Project/                     # ALL project-specific content (never mix with store assets)
│       ├── Art/                      # Source art — not runtime logic
│       │   ├── Characters/           # Character models, textures, animations source
│       │   ├── Environments/         # World geometry, terrain, skyboxes
│       │   ├── Props/                # Interactable and decorative props
│       │   ├── VFX/                  # Particle systems, horror atmosphere effects
│       │   └── UI/                   # UI sprites, fonts, icons
│       │
│       ├── Audio/                    # Runtime audio assets
│       │   ├── Music/                # Adaptive music stems and tracks
│       │   ├── SFX/                  # Interaction, UI, environmental SFX
│       │   ├── Ambience/             # Layered world ambience loops
│       │   └── Mixers/               # Unity AudioMixer assets
│       │
│       ├── Scenes/                   # Unity scene files
│       │   ├── Bootstrap/            # DI composition root scene (loads first)
│       │   ├── Worlds/               # One subfolder per interconnected world
│       │   ├── UI/                   # Persistent UI overlay scenes
│       │   └── Dev/                  # Developer test scenes (excluded from release)
│       │
│       ├── Prefabs/                  # Instantiated runtime objects
│       │   ├── Player/               # Player rig, interaction probe
│       │   ├── NPCs/                 # NPC base prefabs per archetype
│       │   ├── World/                # Triggers, spawners, event volumes
│       │   ├── UI/                   # Screen prefabs
│       │   └── Systems/              # Module system prefabs (audio listener, etc.)
│       │
│       ├── Materials/                # Shared URP materials and shaders refs
│       │
│       ├── Settings/                 # Unity/URP project configuration assets
│       │   ├── URP/                  # Render pipeline assets, renderer features
│       │   ├── Input/                # Input Action Asset(s)
│       │   └── Addressables/         # Addressables groups and settings
│       │
│       ├── ScriptableObjects/        # DATA ONLY — no logic
│       │   ├── Worlds/               # WorldDefinition, WorldConnectionGraph
│       │   ├── NPCs/                 # NpcDefinition, NpcSchedule
│       │   ├── Dialogue/             # Fallback DialogueNode graphs
│       │   ├── Quests/               # QuestDefinition, Objective chains
│       │   ├── Puzzles/              # PuzzleDefinition, strategy bindings
│       │   ├── Narrative/            # StoryBeat, LoreEntry
│       │   ├── Audio/                # AudioCatalog entries
│       │   └── Settings/             # DefaultSettingsProfile
│       │
│       ├── Localization/             # String tables (Unity Localization package)
│       │
│       ├── Scripts/                  # ALL C# code — assembly-segmented
│       │   ├── Core/                 # → Aethras.Core.asmdef
│       │   │   ├── Bootstrap/        # GameBootstrapper (composition root)
│       │   │   ├── DependencyInjection/
│       │   │   ├── Events/           # EventBus impl, event struct definitions
│       │   │   ├── Interfaces/       # IEventBus, IDependencyContainer, etc.
│       │   │   ├── StateMachine/     # Generic FSM implementation
│       │   │   ├── Commands/         # Command dispatcher
│       │   │   ├── Factories/        # Abstract factory helpers
│       │   │   ├── Utilities/        # Pure helpers (math, guards)
│       │   │   ├── Constants/        # Global constants
│       │   │   ├── Extensions/       # Extension methods
│       │   │   └── Logging/          # IGameLogger abstraction
│       │   │
│       │   ├── Domain/               # → Aethras.Domain.asmdef
│       │   │   ├── Entities/         # PlayerState, WorldState, NpcState
│       │   │   ├── ValueObjects/     # ChoiceId, WorldId, MemoryTag
│       │   │   ├── Enums/            # GameStateEnum, PuzzleType
│       │   │   ├── Events/           # Domain events (POCO structs)
│       │   │   ├── Interfaces/       # IRepository<T>, domain services
│       │   │   └── Aggregates/       # SaveGameAggregate, NarrativeAggregate
│       │   │
│       │   ├── Application/          # → Aethras.Application.asmdef
│       │   │   ├── Services/         # Use-case implementations
│       │   │   ├── Commands/         # SaveGameCommand, SubmitChoiceCommand
│       │   │   ├── Queries/          # GetWorldStateQuery
│       │   │   ├── DTOs/             # Cross-boundary data transfer objects
│       │   │   ├── Interfaces/       # IGameOrchestrator, INarrativeService
│       │   │   ├── Mappers/          # Entity ↔ DTO mappers
│       │   │   └── Validators/       # Input validation before domain ops
│       │   │
│       │   ├── Infrastructure/       # → Aethras.Infrastructure.asmdef
│       │   │   ├── Persistence/      # File save/load, PlayerPrefs bridge
│       │   │   ├── Networking/       # HTTP client wrapper (uses AI.Client)
│       │   │   ├── Serialization/    # JSON/binary serializers
│       │   │   ├── Addressables/     # Asset loading wrappers
│       │   │   ├── Repositories/     # IRepository implementations
│       │   │   └── Configuration/    # Backend URL, API keys (ScriptableObject ref)
│       │   │
│       │   ├── Presentation/         # → Aethras.Presentation.asmdef
│       │   │   ├── Views/            # MonoBehaviour view components
│       │   │   ├── ViewModels/       # Bindable state for UI
│       │   │   ├── Presenters/       # View ↔ Application glue
│       │   │   └── UIComponents/     # Reusable UI widgets
│       │   │
│       │   ├── AI/                   # Backend communication (NOT AI logic)
│       │   │   └── Client/           # → Aethras.AI.Client.asmdef
│       │   │       ├── Endpoints/    # Route constants, request builders
│       │   │       ├── DTOs/         # API-specific DTOs
│       │   │       ├── Interfaces/   # IAethrasApiClient
│       │   │       ├── Services/     # ApiClient implementation
│       │   │       └── Mappers/      # API DTO ↔ Application DTO
│       │   │
│       │   ├── Modules/              # Feature modules (21 assemblies)
│       │   │   ├── Player/           # Controllers, Services, Interfaces, Data, Events
│       │   │   ├── Input/
│       │   │   ├── Camera/
│       │   │   ├── World/
│       │   │   ├── Scene/
│       │   │   ├── NPC/
│       │   │   ├── Dialogue/
│       │   │   ├── Quest/
│       │   │   ├── Inventory/
│       │   │   ├── Save/
│       │   │   ├── Narrative/
│       │   │   ├── Choice/
│       │   │   ├── Memory/
│       │   │   ├── Puzzle/           # + Strategies/ subfolder
│       │   │   ├── Audio/
│       │   │   ├── UI/
│       │   │   ├── Loading/
│       │   │   ├── Game/             # + StateMachine/ subfolder
│       │   │   ├── Settings/
│       │   │   ├── Achievement/
│       │   │   └── Analytics/
│       │   │
│       │   └── Editor/               # → Aethras.Editor.asmdef (Editor platform only)
│       │       ├── Tools/            # Batch importers, validators
│       │       ├── Inspectors/       # Custom ScriptableObject inspectors
│       │       ├── Windows/          # Narrative authoring, world graph editor
│       │       └── Build/            # Custom build pipeline hooks
│       │
│       └── Tests/
│           ├── EditMode/             # → Aethras.Tests.EditMode.asmdef
│           └── PlayMode/             # → Aethras.Tests.PlayMode.asmdef
│
├── Packages/                         # Unity Package Manager manifest
└── ProjectSettings/                  # Unity project settings (URP, Input, etc.)
```

### Module Subfolder Convention

Every module under `Scripts/Modules/{Name}/` follows the same structure:

| Subfolder | Purpose |
|-----------|---------|
| `Controllers/` | MonoBehaviours — thin, delegate to Services |
| `Services/` | Business logic for this module |
| `Interfaces/` | Public contract (`I{Name}Service`) |
| `Data/` | ScriptableObject runtime bindings, module config |
| `Events/` | Module-specific event structs for Event Bus |
| `Strategies/` | (Puzzle only) Strategy pattern implementations |
| `StateMachine/` | (Game only) Game state definitions and transitions |

**Why uniform structure:** Any developer can navigate any module instantly; code reviews scale.

---

## Python Backend

```
server/aethras_backend/
├── app/
│   ├── main.py                       # FastAPI app factory, lifespan hooks
│   ├── api/
│   │   ├── routes/                   # /narrative, /memory, /health, /rag
│   │   └── middleware/               # CORS, auth, request logging
│   ├── core/
│   │   ├── config/                   # Pydantic settings (env vars)
│   │   ├── dependencies/             # FastAPI Depends() injection
│   │   ├── exceptions/               # HTTP exception handlers
│   │   └── logging/                  # Structured logging setup
│   ├── narrative/
│   │   ├── engine/                   # Pipeline orchestrator
│   │   ├── models/                   # Pydantic domain models
│   │   └── interfaces/               # INarrativeEngine ABC
│   ├── prompt/
│   │   ├── engine/                   # Template rendering, token count
│   │   ├── templates/                # Jinja2 / string templates
│   │   └── interfaces/               # IPromptEngine ABC
│   ├── rag/
│   │   ├── retriever/                # Vector + keyword retrieval
│   │   ├── embeddings/               # Embedding model wrapper
│   │   └── interfaces/               # IRagRetriever ABC
│   ├── knowledge_graph/
│   │   ├── builder/                  # Graph construction from lore data
│   │   ├── query/                    # Cypher-like or custom graph queries
│   │   └── models/                   # Node/edge models
│   ├── validator/
│   │   ├── rules/                    # Pluggable validation rules
│   │   └── interfaces/               # INarrativeValidator ABC
│   ├── memory_graph/
│   │   ├── store/                    # Player memory persistence
│   │   ├── query/                    # Consequence lookup
│   │   └── models/                   # Memory node models
│   ├── llm/
│   │   ├── providers/                # OpenAI, Ollama, Azure — Strategy pattern
│   │   └── interfaces/               # ILlmProvider ABC
│   ├── schemas/                      # Request/response Pydantic schemas (API contract)
│   └── services/                     # Application services bridging modules
├── tests/
│   ├── unit/
│   └── integration/
├── data/
│   ├── knowledge/                    # Lore JSON/graph source files
│   ├── prompts/                      # Versioned prompt template files
│   └── embeddings/                   # Precomputed embedding indices
├── pyproject.toml
├── requirements.txt
└── README.md
```

**Why separate `schemas/`:** Mirrors Unity Application DTOs; single API contract reference for both teams.

---

## Documentation

```
docs/
├── architecture/                     # System design (this document set)
├── modules/                          # Per-module responsibility docs
├── api/                              # OpenAPI spec, endpoint reference
├── research/                         # Study protocols, metrics definitions
└── adr/                              # Architecture Decision Records
```

---

## Tools & CI

```
tools/
├── build/                            # Unity batch build scripts
├── ci/                               # CI helper scripts
└── scripts/                        # Dev utilities (seed data, mock server)

.github/
├── workflows/                        # unity-build.yml, backend-test.yml
├── ISSUE_TEMPLATE/
└── PULL_REQUEST_TEMPLATE/
```
