import pytest

from .config import client, test_db, authenticated_client

@pytest.mark.asyncio
async def test_get_me(authenticated_client):
    response = await authenticated_client.get("/users/user")

    assert response.status_code == 200
