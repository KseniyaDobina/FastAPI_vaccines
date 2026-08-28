import pytest

from .config import client, test_db, authenticated_client, test_user

@pytest.mark.asyncio
async def test_get_me(authenticated_client, test_user):
    response = await authenticated_client.get("/users/me")

    assert response.status_code == 200
