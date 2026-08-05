import pytest


@pytest.mark.asyncio
async def test_health(test_client):
    response = await test_client.get('/')

    assert response.status_code == 200
    assert response.json()["detail"] == "Hello from Back End!"