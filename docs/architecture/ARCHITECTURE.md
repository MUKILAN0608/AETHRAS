# AETHRAS: Odyssey Beyond the Veil — System Architecture

> **Engine:** Unity 6 LTS · URP · C#  
> **Backend:** Python FastAPI  
> **Target:** Windows Desktop  
> **Status:** Architecture Phase (no gameplay implementation)

---

## 1. Architectural Vision

AETHRAS is designed as a **research-grade, production-scalable** psychological horror adventure. The architecture follows **Clean Architecture** with strict layer separation, **event-driven** inter-module communication, and an **AI backend decoupled from Unity** via REST.

### Guiding Principles

| Principle | Application |
|-----------|-------------|
| **SOLID** | Single-responsibility managers; interface segregation per module |
| **DRY** | Shared Core utilities; Application DTOs; no duplicate persistence logic |
| **KISS** | Modules expose one primary service interface each |
| **Dependency Injection** | Composition root in Bootstrap; constructor injection everywhere |
| **Event Bus** | Cross-module signals; no direct module-to-module references |
| **Repository Pattern** | Domain persistence abstracted; Infrastructure implements |
| **Command Pattern** | Player actions, save/load, narrative submissions |
| **Strategy Pattern** | Puzzle types, LLM providers, validation rules |
| **State Machine** | Game flow, dialogue, puzzles, loading pipeline |
| **Observer Pattern** | Event Bus + UI ViewModels reacting to domain events |

---

## 2. System Architecture Diagram

```mermaid
flowchart TB
    subgraph Client["Unity Client (Windows)"]
        direction TB

        subgraph PresentationLayer["Presentation Layer"]
            Views["Views / UI Components"]
            VMs["ViewModels"]
            Pres["Presenters"]
        end

        subgraph ModuleLayer["Feature Modules (21)"]
            direction LR
            M_Game["Game"]
            M_Player["Player"]
            M_World["World"]
            M_Dialogue["Dialogue"]
            M_Narrative["Narrative"]
            M_Puzzle["Puzzle"]
            M_Others["...17 more"]
        end

        subgraph ApplicationLayer["Application Layer"]
            Orch["IGameOrchestrator"]
            AppSvc["Application Services"]
            Cmds["Commands / Queries"]
            DTOs["DTOs"]
        end

        subgraph DomainLayer["Domain Layer"]
            Entities["Entities / Aggregates"]
            VO["Value Objects"]
            DomEvents["Domain Events"]
            DomRepo["IRepository contracts"]
        end

        subgraph CoreLayer["Core Layer"]
            DI["DI Container"]
            EB["Event Bus"]
            FSM["State Machine"]
            Fact["Factories"]
        end

        subgraph InfraLayer["Infrastructure Layer"]
            Persist["Persistence / Save"]
            Net["HTTP / REST"]
            Ser["Serialization"]
            Addr["Addressables"]
        end

        subgraph AIClientLayer["AI Client Layer"]
            API["IAethrasApiClient"]
            Endpoints["REST Endpoints"]
        end

        Bootstrap["Bootstrap / Composition Root"]
    end

    subgraph Server["Python FastAPI Backend"]
        direction TB
        FastAPI["FastAPI Router"]
        NarrEng["Narrative Engine"]
        PromptEng["Prompt Engine"]
        RAG["RAG Retriever"]
        KG["Knowledge Graph"]
        Val["Narrative Validator"]
        MemG["Memory Graph"]
        LLM["LLM Integration"]
    end

    Bootstrap --> DI
    DI --> ModuleLayer
    ModuleLayer --> ApplicationLayer
    ApplicationLayer --> DomainLayer
    DomainLayer --> CoreLayer
    InfraLayer --> ApplicationLayer
    InfraLayer --> AIClientLayer
    PresentationLayer --> ApplicationLayer
    ModuleLayer -.->|"Events only"| EB
    AIClientLayer -->|"REST/JSON"| FastAPI
    FastAPI --> NarrEng
    NarrEng --> PromptEng
    NarrEng --> RAG
    NarrEng --> KG
    NarrEng --> Val
    NarrEng --> MemG
    PromptEng --> LLM
    RAG --> KG
    MemG --> KG
```

---

## 3. Layer Responsibilities

### Core (`Aethras.Core`)
Foundation with **zero domain knowledge**. Provides DI container, Event Bus, state machine primitives, command interfaces, factories, logging utilities, and constants.

**Why it exists:** Prevents circular dependencies; shared infrastructure for all assemblies.

### Domain (`Aethras.Domain`)
Pure C# domain model: entities, value objects, enums, domain events, repository **contracts**. No UnityEngine references where avoidable.

**Why it exists:** Business rules and data shapes independent of Unity lifecycle.

### Application (`Aethras.Application`)
Use-case orchestration: `IGameOrchestrator`, `INarrativeService`, `ISaveLoadService`, commands, queries, DTOs, validators.

**Why it exists:** Coordinates workflows without UI or transport details.

### Infrastructure (`Aethras.Infrastructure`)
Technical implementations: file I/O, JSON serialization, Addressables wrappers, repository implementations, HTTP bridge to AI.Client.

**Why it exists:** Swappable persistence and networking; keeps modules testable.

### Presentation (`Aethras.Presentation`)
MVVM-style UI: Views, ViewModels, Presenters. Binds to Application services and Event Bus.

**Why it exists:** Separates rendering/input presentation from game logic.

### AI Client (`Aethras.AI.Client`)
REST client, endpoint definitions, request/response DTOs for FastAPI backend.

**Why it exists:** Isolates API contract; enables mock backend for Unity tests.

### Feature Modules (`Aethras.Modules.*`)
One assembly per gameplay system. Each module owns Controllers, Services, Interfaces, Data (ScriptableObject bindings), and Events.

**Why it exists:** Independent development, testing, and hot-swapping of features.

### Editor (`Aethras.Editor`)
Editor-only tools: custom inspectors, build pipelines, narrative authoring aids.

**Why it exists:** Keeps editor code out of player builds.

---

## 4. Data Flow

### 4.1 Exploration Loop

```mermaid
sequenceDiagram
    participant Input as Input Module
    participant EB as Event Bus
    participant Player as Player Module
    participant World as World Manager
    participant NPC as NPC Manager
    participant Dialogue as Dialogue Manager
    participant App as Application Layer
    participant AI as AI Client
    participant API as FastAPI Backend

    Input->>EB: Publish(InputMoveEvent)
    EB->>Player: OnMove
    Player->>World: Update exploration state
    World->>EB: Publish(ProximityEvent)
    EB->>NPC: Check interactable
    NPC->>Dialogue: Request interaction
    Dialogue->>App: INarrativeService.RequestDialogueAsync
    App->>AI: POST /narrative/dialogue
    AI->>API: REST JSON
    API-->>AI: NarrativeResponseDto
    AI-->>App: Mapped response
    App-->>Dialogue: Dialogue lines + choices
    Dialogue->>EB: Publish(DialogueStartedEvent)
```

### 4.2 Permanent Choice Flow

```mermaid
sequenceDiagram
    participant UI as UI Module
    participant Choice as Choice Engine
    participant Memory as Memory Service
    participant Save as Save System
    participant App as Application Layer
    participant API as Memory Graph (Backend)

    UI->>Choice: RecordChoice(choiceId, consequenceTag)
    Choice->>Memory: StoreMemory(consequenceTag)
    Choice->>App: INarrativeService.SubmitChoiceAsync
    App->>API: POST /memory/choice
    API-->>App: Updated memory graph
    App-->>Memory: SyncMemoryAsync
    Memory->>Save: Trigger auto-save snapshot
    Save->>Save: Persist to disk
```

### 4.3 World Load Flow

```mermaid
sequenceDiagram
    participant Game as Game Manager
    participant Loading as Loading Pipeline
    participant Scene as Scene Manager
    participant World as World Manager
    participant Addr as Addressables (Infra)

    Game->>Loading: ExecuteLoadSequenceAsync(worldId)
    Loading->>Scene: LoadSceneAsync(bootstrap)
    Scene->>Addr: Load asset bundle
    Addr-->>Scene: Scene instance
    Loading->>World: LoadWorld(worldId)
    World->>World: Register lore triggers, dynamic events
    Loading->>Game: Publish(WorldLoadedEvent)
```

---

## 5. Communication Diagram

```mermaid
flowchart LR
    subgraph Allowed["Allowed Communication"]
        M1["Module A"] -->|"Interface via DI"| App["Application"]
        M1 -->|"Publish/Subscribe"| EB["Event Bus"]
        M2["Module B"] -->|"Publish/Subscribe"| EB
        App --> Domain["Domain"]
        Infra["Infrastructure"] -->|"Implements"| App
    end

    subgraph Forbidden["Forbidden Communication"]
        M1 -.-x|"NO direct reference"| M2
        Domain -.-x|"NO Unity refs"| Unity["UnityEngine"]
        Modules -.-x|"NO direct HTTP"| API["FastAPI"]
    end
```

### Event Bus Event Categories

| Category | Examples | Publishers | Subscribers |
|----------|----------|------------|-------------|
| Input | `InputMoveEvent`, `InputInteractEvent` | Input | Player, UI |
| World | `WorldLoadedEvent`, `LoreDiscoveredEvent` | World | Narrative, Audio, UI |
| Dialogue | `DialogueStartedEvent`, `DialogueChoiceEvent` | Dialogue | Camera, UI, Choice |
| Narrative | `StoryBeatChangedEvent` | Narrative | Quest, Achievement |
| System | `GamePausedEvent`, `SaveCompletedEvent` | Game, Save | All modules |

---

## 6. Dependency Graph

```mermaid
flowchart BT
    Core["Aethras.Core"]

    Domain["Aethras.Domain"] --> Core
    Application["Aethras.Application"] --> Domain
    Application --> Core

    AIClient["Aethras.AI.Client"] --> Application
    AIClient --> Domain
    AIClient --> Core

    Infrastructure["Aethras.Infrastructure"] --> AIClient
    Infrastructure --> Application
    Infrastructure --> Domain
    Infrastructure --> Core

    Presentation["Aethras.Presentation"] --> Application
    Presentation --> Domain
    Presentation --> Core

    Modules["Aethras.Modules.*"] --> Application
    Modules --> Domain
    Modules --> Core
    ModulesUI["Aethras.Modules.UI"] --> Presentation
    ModulesNarrative["Modules: Dialogue/Narrative/Choice/Memory"] --> AIClient
    ModulesInfra["Modules: Save/Loading/Analytics"] --> Infrastructure

    Editor["Aethras.Editor"] --> Modules
    Editor --> Infrastructure
    Editor --> Presentation

    Tests["Aethras.Tests.*"] --> Core
    Tests --> Application
    Tests --> Infrastructure
```

### Assembly Count Summary

| Assembly | Count | Purpose |
|----------|-------|---------|
| Core layers | 6 | Core, Domain, Application, Infrastructure, Presentation, AI.Client |
| Feature modules | 21 | One per gameplay system |
| Editor | 1 | Editor tooling |
| Tests | 2 | EditMode, PlayMode |
| **Total** | **30** | |

---

## 7. Backend Architecture (Python FastAPI)

```mermaid
flowchart TB
    Router["API Routes (/narrative, /memory, /health)"]
    Router --> NarrativeEngine
    NarrativeEngine --> PromptEngine
    NarrativeEngine --> RAG
    NarrativeEngine --> KnowledgeGraph
    NarrativeEngine --> NarrativeValidator
    NarrativeEngine --> MemoryGraph
    PromptEngine --> LLMProviders["LLM Providers (OpenAI, local, etc.)"]
    RAG --> Embeddings
    RAG --> KnowledgeGraph
    MemoryGraph --> KnowledgeGraph
```

### Backend Module Responsibilities

| Module | Responsibility |
|--------|----------------|
| `narrative/engine` | Orchestrates story generation pipeline |
| `prompt/engine` | Template assembly, token budgeting |
| `prompt/templates` | Version-controlled prompt templates |
| `rag/` | Retrieval-augmented lore/context injection |
| `knowledge_graph/` | World lore, NPC relationships, causal links |
| `validator/` | Ensures AI output respects narrative rules |
| `memory_graph/` | Persistent player choice/consequence graph |
| `llm/providers` | Swappable LLM backends (Strategy pattern) |

---

## 8. Bootstrap & Composition Root

```
Bootstrap Scene
    └── GameBootstrapper (MonoBehaviour — ONLY entry point in scene)
            ├── Creates DependencyContainer
            ├── Registers Core services (EventBus, StateMachine factory)
            ├── Registers Application services
            ├── Registers Infrastructure implementations
            ├── Registers all Module services
            ├── Registers Presentation presenters
            └── Calls IGameOrchestrator.InitializeAsync()
```

**Rule:** `GameBootstrapper` is the only MonoBehaviour allowed to call `Resolve()`. All other classes receive dependencies via constructor injection.

---

## 9. ScriptableObject Strategy

| Folder | Purpose |
|--------|---------|
| `ScriptableObjects/Worlds` | World definitions, connection graph |
| `ScriptableObjects/NPCs` | NPC identity, default dialogue trees |
| `ScriptableObjects/Dialogue` | Fallback non-AI dialogue nodes |
| `ScriptableObjects/Quests` | Objectives, prerequisites, consequences |
| `ScriptableObjects/Puzzles` | Puzzle definitions, strategy type IDs |
| `ScriptableObjects/Narrative` | Story beats, lore entries |
| `ScriptableObjects/Audio` | Music/ambience catalogs |
| `ScriptableObjects/Settings` | Default settings profile |

ScriptableObjects are **data definitions only**. Runtime logic lives in Module Services.

---

## 10. Research Considerations

- **Analytics Module** captures choice distribution, session length, exploration coverage
- **Achievement Module** marks narrative milestones for study cohorts
- **Backend logs** (structured JSON) enable post-session analysis
- **ADR folder** (`docs/adr/`) documents architectural decisions for paper/reports
- **Feature flags** via Settings enable A/B narrative experiments

---

## Related Documents

- [FOLDER_STRUCTURE.md](./FOLDER_STRUCTURE.md) — Complete directory tree with rationale
- [NAMESPACES.md](./NAMESPACES.md) — Namespace conventions
- [ASSEMBLY_DEFINITIONS.md](./ASSEMBLY_DEFINITIONS.md) — Asmdef reference
- [DEPENDENCY_GRAPH.md](./DEPENDENCY_GRAPH.md) — Detailed dependency rules
- [DATA_FLOW.md](./DATA_FLOW.md) — Extended flow documentation
- [COMMUNICATION.md](./COMMUNICATION.md) — Event catalog and API contracts
- [GIT_STRUCTURE.md](./GIT_STRUCTURE.md) — Repository layout
- [../modules/MODULES.md](../modules/MODULES.md) — Per-module responsibilities
