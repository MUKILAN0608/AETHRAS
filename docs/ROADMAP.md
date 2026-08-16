# AETHRAS Roadmap

## PHASE 1: Environment + Communication ✅

- [x] Machine environment inspection
- [x] Godot 4.x project with minimal 3D scene
- [x] Python FastAPI AI service with health endpoint
- [x] Go game server with health endpoint
- [x] Docker Compose (PostgreSQL + Redis)
- [x] Godot → Go → Python communication pipeline
- [x] Mock semantic parser (DEMO / PLACEHOLDER)
- [x] FLOOD visual effect in Godot
- [x] Development scripts and documentation

## PHASE 2: Dynamic Semantic World Engine ✅

- [x] Procedurally generated 3D world (scenario + seed)
- [x] Multiple different initial worlds (3 scenarios)
- [x] Deterministic seeds + reproducibility tests
- [x] Dynamic entities, relationships, terrain
- [x] World event system + causal propagation
- [x] Environmental simulation (tick)
- [x] World history + snapshots
- [x] Semantic transformations (FLOOD, FIRE, MEMORY)
- [x] Dynamic camera + basic visual effects
- [x] Prompt → structured action → world transformation
- [x] No fixed playable map
- [x] Incremental world updates (not full regen)

## PHASE 3: Prompt Intelligence Engine ✅

- [x] Multi-stage pipeline (normalize → intent → entities → strategy → compile → critic → validate)
- [x] Pydantic schemas: ActionProposal, SemanticInterpretation, ValidationResult
- [x] LLM abstraction (MockLLM + Qwen stub)
- [x] Fast / Deep inference path selection
- [x] World context builder (compact state for inference)
- [x] Ambiguity detection + confidence + novelty scoring
- [x] Research experiment logging
- [x] API: `/api/v1/prompt/interpret`, `/validate`, `/compile`, `/health`
- [x] Go interpret + execute endpoints with action taxonomy mapping
- [x] Godot interpret → review → execute async flow
- [x] 28 acceptance tests (idea3.tex §26)

## PHASE 4: Real LLM Integration + Prompt Engineering

- [ ] Connect Qwen3.6-35B-A3B (or local Ollama) via LLMProvider
- [ ] Structured output via Pydantic + JSON mode
- [ ] Prompt engineering experiments
- [ ] Fallback to rule-based pipeline on LLM failure
- [ ] Token budgeting and cost tracking

## PHASE 5: Semantic World (Advanced)

- [ ] Entity-component world model in Go
- [ ] Semantic tagging of world objects
- [ ] Action → state mutation pipeline
- [ ] AI counter-action generation
- [ ] Turn-based game loop

## PHASE 5: Mixture-of-Experts (MoE)

- [ ] Expert routing for action types (environmental, social, combat, puzzle)
- [ ] Expert specialization and load balancing
- [ ] Expert performance metrics

## PHASE 6: Liquid Neural Networks (LNN)

- [ ] Adaptive AI opponent using LNN
- [ ] Continuous-time state adaptation
- [ ] Research benchmarking vs fixed-policy AI

## PHASE 7: World Model

- [ ] Internal world simulation model
- [ ] Predictive state rollout for AI planning
- [ ] "What if" scenario generation

## PHASE 8: VLM / Spatial AI

- [ ] Vision-language model for scene understanding
- [ ] Spatial reasoning about 3D layout
- [ ] Camera-aware prompt interpretation

## PHASE 9: Self-Evolution

- [ ] AI strategy adaptation over multiple matches
- [ ] Player modeling and counter-strategy
- [ ] Safe bounded self-modification

## PHASE 10: Quantum-Inspired Experiments

- [ ] Superposition-inspired action exploration
- [ ] Research-only branch (optional module)

## PHASE 11: Research Benchmarking

- [ ] Standardized evaluation metrics
- [ ] Human vs AI study protocols
- [ ] Reproducible experiment configs
- [ ] Publication-ready data export

---

**Current phase:** Phase 3 complete. Next: Phase 4 (Real LLM Integration).
