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
async def test_user_cannot_update_another_users_vaccine(
    authenticated_client,
    second_user_vaccine,
    vaccine_test_new_data,
):
    original_name = second_user_vaccine.vaccine_name

    response = await authenticated_client.put(
        f"/vaccines/{second_user_vaccine.id}",
        json=vaccine_test_new_data,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Данные о вакцинации не найдены"

    assert second_user_vaccine.vaccine_name == original_name

@pytest.mark.asyncio
async def test_user_cannot_patch_another_users_vaccine(
    authenticated_client,
    second_user_vaccine,
):
    original_notes = second_user_vaccine.notes

    response = await authenticated_client.patch(
        f"/vaccines/{second_user_vaccine.id}",
        json={
            "notes": "Попытка изменить чужую вакцину",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Данные о вакцинации не найдены"

    assert second_user_vaccine.notes == original_notes

@pytest.mark.asyncio
async def test_user_cannot_delete_another_users_vaccine(
    authenticated_client,
    second_user_vaccine,
):
    vaccine_id = second_user_vaccine.id

    response = await authenticated_client.delete(
        f"/vaccines/{vaccine_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Данные о вакцинации не найдены"

    get_response = await authenticated_client.get(
        f"/vaccines/{vaccine_id}"
    )

    assert get_response.status_code == 404
