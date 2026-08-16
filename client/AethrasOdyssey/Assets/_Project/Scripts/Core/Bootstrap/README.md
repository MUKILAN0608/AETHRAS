# Bootstrap

**Namespace:** `Aethras.Core.Bootstrap`

Contains `GameBootstrapper` — the **sole composition root** MonoBehaviour.

Responsibilities:
- Create and configure `IDependencyContainer`
- Register all Core, Application, Infrastructure, and Module services
- Initialize `IGameOrchestrator`
- Load Bootstrap scene as entry point

**Rule:** Only `GameBootstrapper` may call `Resolve()`. All other classes use constructor injection.
