import pytest


@pytest.mark.asyncio
async def test_healthchecker(client):
    response = client.get("/api/healthchecker")

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["status"] == "Database is configured and ready"
