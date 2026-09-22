from httpx import ASGITransport, AsyncClient

from seo_score.api.main import app


async def test_health_returns_json():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code in (200, 503)
    body = response.json()
    assert "postgres" in body
    assert "redis" in body
    assert body["status"] in ("ok", "degraded")
