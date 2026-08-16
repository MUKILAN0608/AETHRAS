"""
FastAPI application factory.

Architecture phase stub — routes and services implemented in next phase.
"""

from fastapi import FastAPI


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="AETHRAS Narrative API",
        description="AI narrative backend for AETHRAS: Odyssey Beyond the Veil",
        version="0.1.0",
    )

    @app.get("/api/v1/health")
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
