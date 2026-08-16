# Assembly Definitions Reference

Unity Assembly Definition (`.asmdef`) files enforce compile-time dependency boundaries. This prevents accidental coupling and reduces iteration time.

---

## Summary Table

| Assembly | Path | Platform | Auto-Referenced |
|----------|------|----------|-----------------|
| `Aethras.Core` | `Scripts/Core/` | All | Yes |
| `Aethras.Domain` | `Scripts/Domain/` | All | Yes |
| `Aethras.Application` | `Scripts/Application/` | All | Yes |
| `Aethras.Infrastructure` | `Scripts/Infrastructure/` | All | Yes |
| `Aethras.Presentation` | `Scripts/Presentation/` | All | Yes |
| `Aethras.AI.Client` | `Scripts/AI/Client/` | All | Yes |
| `Aethras.Modules.*` | `Scripts/Modules/{Name}/` | All | Yes |
| `Aethras.Editor` | `Scripts/Editor/` | Editor only | No |
| `Aethras.Tests.EditMode` | `Tests/EditMode/` | Editor only | No |
| `Aethras.Tests.PlayMode` | `Tests/PlayMode/` | All | No |

---

## Layer Assemblies

### Aethras.Core
- **References:** None (foundation)
- **Purpose:** DI, Event Bus, FSM, Commands, Utilities
- **Rule:** Must NOT reference Unity gameplay assemblies or any module

### Aethras.Domain
- **References:** `Aethras.Core`
- **Purpose:** Pure domain model and repository contracts
- **Rule:** Minimize `UnityEngine` usage; prefer pure C#

### Aethras.Application
- **References:** `Aethras.Core`, `Aethras.Domain`
- **Purpose:** Use cases, orchestrators, DTOs, command/query handlers
- **Rule:** No MonoBehaviour, no HTTP, no file I/O

### Aethras.Infrastructure
- **References:** `Aethras.Core`, `Aethras.Domain`, `Aethras.Application`, `Aethras.AI.Client`
- **Purpose:** Persistence, serialization, Addressables, HTTP bridge
- **Rule:** Implements Application/Domain interfaces only

### Aethras.Presentation
- **References:** `Aethras.Core`, `Aethras.Domain`, `Aethras.Application`
- **Purpose:** MVVM UI layer
- **Rule:** Views bind to ViewModels; Presenters call Application services

### Aethras.AI.Client
- **References:** `Aethras.Core`, `Aethras.Domain`, `Aethras.Application`
- **Purpose:** REST transport to FastAPI backend
- **Rule:** No narrative logic — transport and mapping only

---

## Module Assemblies (21)

### Standard References
All modules reference:
```
Aethras.Core
Aethras.Domain
Aethras.Application
```

### Extended References (by module)

| Module | Additional References | Reason |
|--------|----------------------|--------|
| `UI` | `Aethras.Presentation` | MVVM binding |
| `Dialogue` | `Aethras.AI.Client` | Dialogue API calls (via typed client) |
| `Narrative` | `Aethras.AI.Client` | Story beat sync |
| `Choice` | `Aethras.AI.Client` | Choice submission |
| `Memory` | `Aethras.AI.Client` | Memory graph sync |
| `Save` | `Aethras.Infrastructure` | File persistence access |
| `Loading` | `Aethras.Infrastructure` | Addressables loading |
| `Analytics` | `Aethras.Infrastructure` | Telemetry export |

**Note:** Even modules with AI.Client reference should prefer `INarrativeService` from Application for business calls. Direct AI.Client usage is limited to module-internal adapters.

---

## Editor Assembly

### Aethras.Editor
- **Platform:** Editor only
- **References:** All layer + module assemblies
- **Purpose:** Custom inspectors, build tools, authoring windows
- **Rule:** Never included in player builds

---

## Test Assemblies

### Aethras.Tests.EditMode
- **Platform:** Editor
- **References:** Core layers + `UnityEngine.TestRunner`
- **Purpose:** Unit tests for Domain, Application, Infrastructure

### Aethras.Tests.PlayMode
- **Platform:** All
- **References:** Core layers + selected modules (Game, Player, World)
- **Purpose:** Integration tests in play mode

---

## Dependency Rules (Enforced by Design)

```
✅ Allowed:
   Module → Application → Domain → Core
   Infrastructure → Application
   Module → Event Bus (Core)
   Editor → Everything

❌ Forbidden:
   Module → Module (direct)
   Domain → Application
   Core → anything above
   Application → Infrastructure
   Application → Modules
```

---

## Adding a New Module Checklist

1. Create folder under `Scripts/Modules/{NewModule}/` with standard subfolders
2. Add `Aethras.Modules.{NewModule}.asmdef` with standard references
3. Add namespace entries to `NAMESPACES.md`
4. Add module doc to `docs/modules/MODULES.md`
5. Register services in Bootstrap composition root
6. Add optional reference in `Aethras.Editor.asmdef`
7. Create `I{NewModule}Service` interface in module's `Interfaces/` folder
