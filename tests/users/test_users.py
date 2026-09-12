import pytest
from sqlalchemy import select

from app_vaccines.models.db_models import User
from tests.config import client, test_db, authenticated_client, test_user, authenticated_client_new_user


@pytest.mark.asyncio
async def test_get_me(authenticated_client, test_user):
    response = await authenticated_client.get("/users/me")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_user_success(authenticated_client_new_user, test_db):
    response = await authenticated_client_new_user.post("/users")

    assert response.status_code == 201

    body = response.json()
    assert body["user"]["username"] == "brand_new_user"
    assert body["user"]["email"] == "brand_new@example.com"
    assert "id" in body["user"]

    # Проверяем не только ответ API, но и реальное состояние БД -
    # чтобы убедиться, что пользователь не просто "как будто создался"
    # в ответе, а действительно записан
    result = await test_db.execute(
        select(User).where(User.keycloak_id == "brand-new-keycloak-id")
    )
    user_in_db = result.scalar_one_or_none()
    assert user_in_db is not None
    assert user_in_db.username == "brand_new_user"


@pytest.mark.asyncio
async def test_create_user_conflict_if_already_exists(authenticated_client):
    """
    authenticated_client уже подразумевает test_user - пользователь
    с sub="test-keycloak-id" уже существует в БД до этого запроса.
    """
    response = await authenticated_client.post("/users")

    assert response.status_code == 409
    assert response.json()["detail"] == "Пользователь уже создан"

