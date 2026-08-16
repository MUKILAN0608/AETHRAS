# Namespace Conventions

All C# code uses the root namespace **`Aethras`**. Namespaces mirror folder paths and assembly boundaries.

---

## Pattern

```
Aethras.{Layer}.{OptionalModule}.{SubArea}
```

| Segment | Description | Example |
|---------|-------------|---------|
| `Aethras` | Root brand namespace | — |
| `{Layer}` | Architectural layer or `Modules` | `Core`, `Domain`, `Modules` |
| `{OptionalModule}` | Module name when in Modules layer | `Dialogue`, `World` |
| `{SubArea}` | Functional subfolder | `Interfaces`, `Services`, `Events` |

---

## Layer Namespaces

### Core Layer — Assembly: `Aethras.Core`

```
Aethras.Core.Bootstrap
Aethras.Core.DependencyInjection
Aethras.Core.Events
Aethras.Core.Interfaces
Aethras.Core.StateMachine
Aethras.Core.Commands
Aethras.Core.Factories
Aethras.Core.Utilities
Aethras.Core.Constants
Aethras.Core.Extensions
Aethras.Core.Logging
```

### Domain Layer — Assembly: `Aethras.Domain`

```
Aethras.Domain.Entities
Aethras.Domain.ValueObjects
Aethras.Domain.Enums
Aethras.Domain.Events
Aethras.Domain.Interfaces
Aethras.Domain.Aggregates
```

### Application Layer — Assembly: `Aethras.Application`

```
Aethras.Application.Services
Aethras.Application.Commands
Aethras.Application.Queries
Aethras.Application.DTOs
Aethras.Application.Interfaces
Aethras.Application.Mappers
Aethras.Application.Validators
```

### Infrastructure Layer — Assembly: `Aethras.Infrastructure`

```
Aethras.Infrastructure.Persistence
Aethras.Infrastructure.Networking
Aethras.Infrastructure.Serialization
Aethras.Infrastructure.Addressables
Aethras.Infrastructure.Repositories
Aethras.Infrastructure.Configuration
```

### Presentation Layer — Assembly: `Aethras.Presentation`

```
Aethras.Presentation.Views
Aethras.Presentation.ViewModels
Aethras.Presentation.Presenters
Aethras.Presentation.UIComponents
```

### AI Client Layer — Assembly: `Aethras.AI.Client`

```
Aethras.AI.Client.Endpoints
Aethras.AI.Client.DTOs
Aethras.AI.Client.Interfaces
Aethras.AI.Client.Services
Aethras.AI.Client.Mappers
```

---

## Module Namespaces — Assembly: `Aethras.Modules.{Name}`

Each module uses a consistent sub-namespace set:

```
Aethras.Modules.{Name}.Controllers
Aethras.Modules.{Name}.Services
Aethras.Modules.{Name}.Interfaces
Aethras.Modules.{Name}.Data
Aethras.Modules.{Name}.Events
```

### Special Sub-Namespaces

```
Aethras.Modules.Puzzle.Strategies      # IPuzzleStrategy implementations
Aethras.Modules.Game.StateMachine      # Game state enum + transition rules
```

### Complete Module List

| Module | Root Namespace |
|--------|----------------|
| Player | `Aethras.Modules.Player` |
| Input | `Aethras.Modules.Input` |
| Camera | `Aethras.Modules.Camera` |
| World | `Aethras.Modules.World` |
| Scene | `Aethras.Modules.Scene` |
| NPC | `Aethras.Modules.NPC` |
| Dialogue | `Aethras.Modules.Dialogue` |
| Quest | `Aethras.Modules.Quest` |
| Inventory | `Aethras.Modules.Inventory` |
| Save | `Aethras.Modules.Save` |
| Narrative | `Aethras.Modules.Narrative` |
| Choice | `Aethras.Modules.Choice` |
| Memory | `Aethras.Modules.Memory` |
| Puzzle | `Aethras.Modules.Puzzle` |
| Audio | `Aethras.Modules.Audio` |
| UI | `Aethras.Modules.UI` |
| Loading | `Aethras.Modules.Loading` |
| Game | `Aethras.Modules.Game` |
| Settings | `Aethras.Modules.Settings` |
| Achievement | `Aethras.Modules.Achievement` |
| Analytics | `Aethras.Modules.Analytics` |

---

## Editor & Test Namespaces

```
Aethras.Editor.Tools
Aethras.Editor.Inspectors
Aethras.Editor.Windows
Aethras.Editor.Build

Aethras.Tests.EditMode.{ModuleUnderTest}
Aethras.Tests.PlayMode.{ModuleUnderTest}
```

---

## Python Backend Namespaces (Package Convention)

Python uses flat package modules under `app/`:

```
app.narrative.engine
app.prompt.engine
app.rag.retriever
app.knowledge_graph.query
app.validator.rules
app.memory_graph.store
app.llm.providers
app.schemas
app.services
```

---

## Rules

1. **One namespace per folder** — folder path determines namespace.
2. **No global usings pollution** — explicit imports in each file.
3. **Interfaces live in `.Interfaces` sub-namespace** — never mixed with implementations.
4. **Event structs live in `.Events`** — suffix with `Event` (e.g., `DialogueStartedEvent`).
5. **DTOs never leak into Domain** — Application layer owns DTOs.
6. **ScriptableObjects** use `Aethras.Modules.{Name}.Data` or dedicated SO namespace.
7. **No `Aethras.Modules.X` importing `Aethras.Modules.Y`** — use Event Bus or Application services.
