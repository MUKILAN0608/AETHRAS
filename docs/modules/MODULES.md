# Module Responsibilities

Single-responsibility reference for all AETHRAS modules.  
**No module may become a God class** — split into Services when complexity grows.

---

## Orchestration

### Game Module (`Aethras.Modules.Game`)
**Single Responsibility:** Top-level game lifecycle and state machine.

| Component | Responsibility |
|-----------|----------------|
| `IGameStateService` | State transitions: Bootstrap → MainMenu → Loading → Exploration → Dialogue → Puzzle → Paused |
| `GameOrchestrator` (impl of `IGameOrchestrator`) | Initializes modules in correct order |
| State Machine | Guards invalid transitions (e.g., no save during dialogue) |

**Depends on:** All module interfaces (via DI at orchestration level only)  
**Publishes:** `GameInitializedEvent`, `GamePausedEvent`, `GameResumedEvent`

---

## Player & Input

### Player Module (`Aethras.Modules.Player`)
**Single Responsibility:** Player locomotion, interaction probing, exploration state.

| Interface | Responsibility |
|-----------|----------------|
| `IPlayerController` | Movement enable/disable, interaction enable/disable |

**Does NOT:** Handle input binding (Input Module), camera (Camera Module), or dialogue (Dialogue Module).

### Input Module (`Aethras.Modules.Input`)
**Single Responsibility:** Unity Input System abstraction and input event publishing.

| Interface | Responsibility |
|-----------|----------------|
| `IInputService` | Enable/disable input, rebinding |

**Publishes:** `InputMoveEvent`, `InputInteractEvent`, `InputPauseEvent`

### Camera Module (`Aethras.Modules.Camera`)
**Single Responsibility:** Camera modes and cinematic blending.

| Interface | Responsibility |
|-----------|----------------|
| `ICameraDirector` | Exploration, dialogue, puzzle camera presets |

**Subscribes to:** `DialogueStartedEvent`, `PuzzleStartedEvent`, `DialogueEndedEvent`

---

## World & Scene

### World Manager (`Aethras.Modules.World`)
**Single Responsibility:** Interconnected world instances, lore triggers, dynamic events.

| Interface | Responsibility |
|-----------|----------------|
| `IWorldManager` | Load/unload worlds, register dynamic events |

**Owns:** World connection graph references (ScriptableObjects)  
**Publishes:** `WorldLoadedEvent`, `LoreDiscoveredEvent`, `DynamicEventTriggeredEvent`

### Scene Manager (`Aethras.Modules.Scene`)
**Single Responsibility:** Async/additive scene loading via Addressables.

| Interface | Responsibility |
|-----------|----------------|
| `ISceneLoader` | Load/unload scenes, report progress |

**Does NOT:** Apply world game state (World Manager does that after load).

### Loading System (`Aethras.Modules.Loading`)
**Single Responsibility:** Unified loading pipeline orchestration.

| Interface | Responsibility |
|-----------|----------------|
| `ILoadingPipeline` | Multi-step load sequences with progress reporting |

**Coordinates:** Scene Manager, World Manager, optional AI warm-up ping.

---

## Characters & Interaction

### NPC Manager (`Aethras.Modules.NPC`)
**Single Responsibility:** NPC spawn registry and availability state.

| Interface | Responsibility |
|-----------|----------------|
| `INpcManager` | Register/unregister NPC instances, availability flags |

**Does NOT:** Run dialogue (Dialogue Module) or AI (Application Layer).

### Dialogue Manager (`Aethras.Modules.Dialogue`)
**Single Responsibility:** Dialogue flow, branching, AI response display.

| Interface | Responsibility |
|-----------|----------------|
| `IDialogueManager` | Start/advance/end dialogue sessions |

**Uses:** `INarrativeService` for AI responses; fallback ScriptableObject dialogue trees.

---

## Narrative Systems

### Narrative Engine (Client) (`Aethras.Modules.Narrative`)
**Single Responsibility:** Client-side story beat tracking and lore registry.

| Interface | Responsibility |
|-----------|----------------|
| `INarrativeStateService` | Current beat, lore discovery flags |

**Note:** AI narrative *generation* lives on backend. This module tracks *state*.

### Choice Engine (`Aethras.Modules.Choice`)
**Single Responsibility:** Permanent choice recording and consequence tagging.

| Interface | Responsibility |
|-----------|----------------|
| `IChoiceEngine` | Record choices, query consequence tags |

**Publishes:** `ChoiceRecordedEvent`, `ConsequenceAppliedEvent`

### Memory System (`Aethras.Modules.Memory`)
**Single Responsibility:** Local memory graph cache synced with backend.

| Interface | Responsibility |
|-----------|----------------|
| `IMemoryService` | Store/retrieve memory tags, sync operations |

**Uses:** `INarrativeService.SyncMemoryAsync`

---

## Progression

### Quest Manager (`Aethras.Modules.Quest`)
**Single Responsibility:** Quest lifecycle and permanent world consequences.

| Interface | Responsibility |
|-----------|----------------|
| `IQuestManager` | Start quests, complete objectives, apply consequences |

**Subscribes to:** `ChoiceRecordedEvent`, `PuzzleCompletedEvent`, `LoreDiscoveredEvent`

### Inventory (`Aethras.Modules.Inventory`)
**Single Responsibility:** Lore items, keys, narrative objects (no combat gear).

| Interface | Responsibility |
|-----------|----------------|
| `IInventoryService` | Add/remove/query items |

### Achievement Manager (`Aethras.Modules.Achievement`)
**Single Responsibility:** Milestone tracking for research and player reward.

| Interface | Responsibility |
|-----------|----------------|
| `IAchievementService` | Unlock, query, progress |

---

## Gameplay Framework

### Puzzle Framework (`Aethras.Modules.Puzzle`)
**Single Responsibility:** Puzzle lifecycle with Strategy pattern for types.

| Interface | Responsibility |
|-----------|----------------|
| `IPuzzleController` | Start/submit/abort puzzles |
| `IPuzzleStrategy` | Type-specific validation and hooks |

**Strategies folder:** One class per puzzle type (symbol, sequence, environmental, etc.)

---

## Persistence & Settings

### Save System (`Aethras.Modules.Save`)
**Single Responsibility:** Save coordination and auto-save triggers.

| Interface | Responsibility |
|-----------|----------------|
| `ISaveCoordinator` | Request saves, gate save availability |

**Delegates to:** Application `ISaveLoadService` → Infrastructure persistence.

### Settings Manager (`Aethras.Modules.Settings`)
**Single Responsibility:** Graphics, audio, accessibility, input settings.

| Interface | Responsibility |
|-----------|----------------|
| `ISettingsService` | Get/set/apply/reset settings |

---

## Presentation & Audio

### UI Framework (`Aethras.Modules.UI`)
**Single Responsibility:** UI screen stack, modals, HUD visibility.

| Interface | Responsibility |
|-----------|----------------|
| `IUiStackService` | Push/pop screens and modals |

**Works with:** Presentation layer ViewModels.

### Audio System (`Aethras.Modules.Audio`)
**Single Responsibility:** Layered music, ambience, SFX, adaptive horror intensity.

| Interface | Responsibility |
|-----------|----------------|
| `IAudioDirector` | Play tracks, set adaptive intensity |

**Subscribes to:** `WorldLoadedEvent`, `DialogueStartedEvent`, world horror triggers.

---

## Research & Telemetry

### Analytics (`Aethras.Modules.Analytics`)
**Single Responsibility:** Research telemetry collection and batch export.

| Interface | Responsibility |
|-----------|----------------|
| `IAnalyticsService` | Track events, session lifecycle, flush |

**Subscribes to:** Choice, exploration, dialogue, and session events.

---

## Backend AI Modules (Python)

| Module | Single Responsibility |
|--------|----------------------|
| **Narrative Engine** | Orchestrate full generation pipeline |
| **Prompt Engine** | Assemble prompts from templates + context |
| **RAG** | Retrieve relevant lore from vector + graph store |
| **Knowledge Graph** | Store/query world lore, NPC relations, causality |
| **Narrative Validator** | Enforce canon, tone, horror guidelines |
| **Memory Graph** | Persist/query player choices across sessions |
| **LLM Integration** | Swappable provider abstraction |

---

## Module Size Guidelines

| Metric | Threshold | Action |
|--------|-----------|--------|
| Service class lines | > 300 | Split into focused services |
| Interface methods | > 10 | Segregate interface (ISP) |
| Event subscribers per module | > 15 | Consider facade subscriber |
| Direct DI dependencies | > 6 | Review SRP violation |
