import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health(client: AsyncClient):
    r = await client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in ("healthy", "degraded")
    assert "uptime_seconds" in data


@pytest.mark.anyio
async def test_list_geo_entities(client: AsyncClient):
    r = await client.get("/api/v1/geo")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
