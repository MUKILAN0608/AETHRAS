# AETHRAS Backend — Python FastAPI AI Narrative Server

Independent from Unity. Communicates via REST/JSON.

## Structure

See `docs/architecture/FOLDER_STRUCTURE.md` for full layout.

## Modules

- `narrative/` — Pipeline orchestrator
- `prompt/` — Template engine
- `rag/` — Retrieval-augmented generation
- `knowledge_graph/` — Lore and causality graph
- `validator/` — Narrative rule enforcement
- `memory_graph/` — Player choice persistence
- `llm/` — LLM provider abstraction

## Setup (Next Phase)

```bash
cd server/aethras_backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
