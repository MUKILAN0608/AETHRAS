"""Tests for AI service health and mock parser."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "aethras-ai"
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_parse_ocean_rises() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/parse",
            json={"prompt": "The ocean rises."},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "FLOOD"
    assert data["demo"] is True


@pytest.mark.asyncio
async def test_parse_forest_fire() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/parse",
            json={"prompt": "The forest catches fire."},
        )
    data = response.json()
    assert data["action"] == "FIRE"
    assert data["target"] == "FOREST"


@pytest.mark.asyncio
async def test_parse_mountain_lie() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/parse",
            json={"prompt": "The mountain remembers this lie."},
        )
    data = response.json()
    assert data["action"] == "MEMORY_REMEMBER"
    assert data["target"] == "MOUNTAIN"
