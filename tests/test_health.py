import pytest

@pytest.mark.asyncio
async def test_healthcheck_endpoint(async_client):
    response = await async_client.get("/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "Aegis-LLM-Gateway"