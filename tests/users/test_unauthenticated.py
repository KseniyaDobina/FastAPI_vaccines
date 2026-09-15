import pytest


@pytest.mark.parametrize(
    ("method", "url"),
    [
        ("get", "/users/me"),
        ("post", "/users")
    ],
)
@pytest.mark.asyncio
async def test_users_endpoints_without_auth(client, method, url):
    response = await getattr(client, method)(url)

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
