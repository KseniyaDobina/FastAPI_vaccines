import pytest

from tests.config import client, test_db, authenticated_client, second_user_vaccine, second_user


@pytest.mark.asyncio
async def test_user_cannot_get_another_users_vaccine(
    authenticated_client,
    second_user_vaccine,
):
    response = await authenticated_client.get(
        f"/vaccines/{second_user_vaccine.id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Данные о вакцинации не найдены"


@pytest.mark.asyncio
async def test_user_cannot_delete_another_users_vaccine(
    authenticated_client,
    second_user_vaccine,
):
    response = await authenticated_client.delete(
        f"/vaccines/{second_user_vaccine.id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Данные о вакцинации не найдены"
