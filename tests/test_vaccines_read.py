import pytest

from tests.config import client, test_db
from tests.conftest import vaccine_in_db

@pytest.mark.asyncio
async def test_get_all_vaccines(client):
    """
    Тест на получение списка всех записей о вакцинации
    """

    response = await client.get("/vaccines")
    data = response.json()

    assert "message" in data
    assert "vaccines" in data
    assert isinstance(data["message"], str)
    assert isinstance(data["vaccines"], list)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_vaccine(client, vaccine_in_db):
    """
    Получение существующей вакцинации по ID
    """

    response = await client.get(
        f"/vaccines/{vaccine_in_db.id}"
    )

    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert "vaccine" in data
    vaccine = data["vaccine"]

    assert vaccine["id"] == vaccine_in_db.id
    assert vaccine["disease"] == "COVID-19"
    assert vaccine["vaccine_name"] == "Comirnaty"
    assert vaccine["dose_number"] == "1"
    assert vaccine["vaccination_date"] == "2026-08-20"
    assert vaccine["expiration_date"] == "2027-01-31"
    assert vaccine["type_vaccine"] == "mRNA"
    assert vaccine["lot"] == "ABC12345"
    assert vaccine["manufacturer"] == "Pfizer-BioNTech"
    assert vaccine["clinic"] == "City Medical Center"
    assert vaccine["country"] == "Germany"
    assert vaccine["city"] == "Frankfurt am Main"
    assert vaccine["notes"] == "Вакцинация проведена без осложнений"

@pytest.mark.asyncio
async def test_get_vaccine_not_found(client):
    """
    Получение вакцинации, которой не существует
    """

    response = await client.get("/vaccines/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Данные о вакцинации не найдены"