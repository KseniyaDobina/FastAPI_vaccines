import pytest

from tests.config import client, test_db

@pytest.mark.parametrize(
    "method,url",
    [
        ("get", "/vaccines"),
        ("post", "/vaccines"),
        ("get", "/vaccines/1"),
        ("put", "/vaccines/1"),
        ("patch", "/vaccines/1"),
        ("delete", "/vaccines/1"),
    ],
)
@pytest.mark.asyncio
async def test_vaccines_endpoints_without_auth(client, method, url):
    response = await getattr(client, method)(url)

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
