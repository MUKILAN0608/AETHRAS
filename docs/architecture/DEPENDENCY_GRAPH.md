# Dependency Graph

Detailed compile-time and runtime dependency rules for AETHRAS.

---

## Compile-Time Dependency Graph

```mermaid
flowchart BT
    subgraph Tier0["Tier 0 — Foundation"]
        Core["Aethras.Core"]
    end

    subgraph Tier1["Tier 1 — Domain"]
        Domain["Aethras.Domain"]
    end

    subgraph Tier2["Tier 2 — Application"]
        Application["Aethras.Application"]
    end

    subgraph Tier3["Tier 3 — Adapters"]
        AIClient["Aethras.AI.Client"]
        Presentation["Aethras.Presentation"]
    end

    subgraph Tier4["Tier 4 — Infrastructure"]
        Infrastructure["Aethras.Infrastructure"]
    end

    subgraph Tier5["Tier 5 — Features"]
        M_Standard["Modules (standard)"]
        M_UI["Modules.UI"]
        M_AI["Modules: Dialogue/Narrative/Choice/Memory"]
        M_Infra["Modules: Save/Loading/Analytics"]
    end

    subgraph Tier6["Tier 6 — Tooling"]
        Editor["Aethras.Editor"]
        TestsE["Tests.EditMode"]
        TestsP["Tests.PlayMode"]
    end

    Domain --> Core
    Application --> Domain
    Application --> Core
    AIClient --> Application
    AIClient --> Domain
    AIClient --> Core
    Presentation --> Application
    Presentation --> Domain
    Presentation --> Core
    Infrastructure --> AIClient
    Infrastructure --> Application
    Infrastructure --> Domain
    Infrastructure --> Core

    M_Standard --> Application
    M_Standard --> Domain
    M_Standard --> Core
    M_UI --> Presentation
    M_AI --> AIClient
    M_Infra --> Infrastructure

    Editor --> M_Standard
    Editor --> Infrastructure
    TestsE --> Application
    TestsP --> M_Standard
```

---

## Runtime Dependency Graph (DI)

At runtime, the **Composition Root** (`GameBootstrapper`) wires interfaces to implementations:

```mermaid
flowchart TD
    Bootstrap["GameBootstrapper"]

    Bootstrap --> EventBus["IEventBus → EventBus"]
    Bootstrap --> Container["IDependencyContainer"]

    Bootstrap --> GameOrch["IGameOrchestrator → GameOrchestrator"]
    Bootstrap --> NarrativeSvc["INarrativeService → NarrativeService"]
    Bootstrap --> SaveSvc["ISaveLoadService → SaveLoadService"]

    Bootstrap --> ApiClient["IAethrasApiClient → AethrasApiClient"]
    Bootstrap --> SaveRepo["ISaveRepository → FileSaveRepository"]

    Bootstrap --> WorldMgr["IWorldManager → WorldManager"]
    Bootstrap --> DialogueMgr["IDialogueManager → DialogueManager"]
    Bootstrap --> PlayerCtrl["IPlayerController → PlayerController"]
    Bootstrap --> ChoiceEng["IChoiceEngine → ChoiceEngine"]

    NarrativeSvc --> ApiClient
    SaveSvc --> SaveRepo
    DialogueMgr --> NarrativeSvc
    ChoiceEng --> NarrativeSvc
```

---

## Module Interaction Matrix

Rows = consumer, Columns = provider.  
✅ = via interface/DI, 📡 = via Event Bus only, ❌ = forbidden

| Consumer ↓ / Provider → | Player | World | Dialogue | Choice | Save | Narrative | UI | Game |
|-------------------------|--------|-------|----------|--------|------|-----------|-----|------|
| Player | — | 📡 | ❌ | ❌ | ❌ | ❌ | ❌ | 📡 |
| World | 📡 | — | 📡 | ❌ | ❌ | 📡 | ❌ | 📡 |
| Dialogue | ❌ | ❌ | — | 📡 | ❌ | ✅ App | 📡 | 📡 |
| Choice | ❌ | 📡 | 📡 | — | 📡 | ✅ App | ❌ | 📡 |
| Save | ❌ | ❌ | ❌ | ❌ | — | ❌ | ❌ | 📡 |
| UI | ❌ | ❌ | 📡 | ❌ | ❌ | ❌ | — | 📡 |
| Game | ✅ DI | ✅ DI | ✅ DI | ❌ | ✅ DI | ❌ | ✅ DI | — |

**Key:** `Game` module (orchestrator) is the only module permitted to directly inject multiple module interfaces — it acts as the high-level coordinator via `IGameOrchestrator`.

---

## Backend Dependency Graph

```mermaid
flowchart BT
    FastAPI["FastAPI App"]
    Routes["API Routes"]
    Services["App Services"]

    NarrativeEngine["Narrative Engine"]
    PromptEngine["Prompt Engine"]
    RAG["RAG Retriever"]
    KnowledgeGraph["Knowledge Graph"]
    Validator["Narrative Validator"]
    MemoryGraph["Memory Graph"]
    LLM["LLM Provider"]

    FastAPI --> Routes
    Routes --> Services
    Services --> NarrativeEngine
    NarrativeEngine --> PromptEngine
    NarrativeEngine --> RAG
    NarrativeEngine --> Validator
    NarrativeEngine --> MemoryGraph
    PromptEngine --> LLM
    RAG --> KnowledgeGraph
    RAG --> Embeddings["Embedding Model"]
    MemoryGraph --> KnowledgeGraph
    Validator --> KnowledgeGraph
```

---

## Circular Dependency Prevention

| Risk | Prevention |
|------|------------|
| Module A ↔ Module B | Event Bus only |
| Domain ↔ Application | Strict one-way: App depends on Domain |
| Unity ↔ Domain | Domain entities avoid MonoBehaviour |
| Client ↔ Server types | Separate DTOs; shared OpenAPI spec in `docs/api/` |
| Narrative ↔ Dialogue | Both use Application `INarrativeService` |

---

## Service Locator Policy

**Default:** Constructor injection via `IDependencyContainer` at bootstrap.

**Service Locator permitted only for:**
- `GameBootstrapper` (composition root)
- Editor tooling (optional `EditorServiceLocator` in `Aethras.Editor`)
- Unity serialization callbacks where DI is unavailable (document with ADR)

**Never use Service Locator in:** Module Services, Application Services, Domain logic.
