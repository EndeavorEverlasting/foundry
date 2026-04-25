import pytest
from httpx import ASGITransport, AsyncClient

from foundry_api.main import create_app


@pytest.mark.asyncio
async def test_health_returns_ok() -> None:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/health")
    assert r.status_code == 200
    payload = r.json()
    assert payload["status"] == "ok"
    assert "version" in payload
