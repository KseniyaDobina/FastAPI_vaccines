import pytest

from tests.config import client, test_db

@pytest.mark.asyncio
async def test_get_all_vaccines(client):
    """
    Тест на получение списка всех записей о вакцинации.
    """

    response = await client.get("/vaccines")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_without_data(client):
    """
    Проверка валидации входных данных.
    """

    response = await client.post("/vaccines")

    assert response.status_code == 422


@pytest.fixture
def vaccine_data():
    return {
        "disease": "COVID-19",
        "vaccine_name": "Sputnik V",
        "clinic": "Поликлиника №1",
        "country": "Россия",
        "city": "Москва",
    }


@pytest.mark.asyncio
async def test_post_create_vaccine(client, vaccine_data):
    """
    Проверка создания записи о вакцинации.
    """

    response = await client.post(
        "/vaccines",
        json=vaccine_data,
    )

    assert response.status_code == 201
