# Architecture Decision Record

## ADR-0001: Monorepo with Clean Architecture

**Status:** Accepted  
**Date:** 2026-07-25

### Context

AETHRAS requires Unity client + Python AI backend with shared API contracts, research reproducibility, and scalable team development.

### Decision

- Monorepo with `client/`, `server/`, `docs/` folders
- Unity code organized in Clean Architecture layers with 21 feature module assemblies
- Inter-module communication via Event Bus only (no direct module references)
- Backend decoupled via REST API with OpenAPI spec in `docs/api/`

### Consequences

- Atomic commits across client and server
- 30 assembly definitions to maintain
- Slightly higher initial setup cost, significantly lower long-term coupling
