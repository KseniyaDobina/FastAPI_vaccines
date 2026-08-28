import pytest

from tests.config import client, test_db, authenticated_client, test_user
from tests.conftest import vaccine_in_db

@pytest.mark.asyncio
async def test_get_all_vaccines(authenticated_client):
    """
    Тест на получение списка всех записей о вакцинации
    """

    response = await authenticated_client.get("/vaccines")
    data = response.json()

    assert isinstance(data, list)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_vaccine(authenticated_client, vaccine_in_db):
    """
    Получение существующей вакцинации по ID
    """

    response = await authenticated_client.get(
        f"/vaccines/{vaccine_in_db.id}"
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == vaccine_in_db.id
    assert data["disease"] == "COVID-19"
    assert data["vaccine_name"] == "Comirnaty"
    assert data["dose_number"] == "1"
    assert data["vaccination_date"] == "2026-08-20"
    assert data["expiration_date"] == "2027-01-31"
    assert data["type_vaccine"] == "mRNA"
    assert data["lot"] == "ABC12345"
    assert data["manufacturer"] == "Pfizer-BioNTech"
    assert data["clinic"] == "City Medical Center"
    assert data["country"] == "Germany"
    assert data["city"] == "Frankfurt am Main"
    assert data["notes"] == "Вакцинация проведена без осложнений"

@pytest.mark.asyncio
async def test_get_vaccine_not_found(authenticated_client):
    """
    Получение вакцинации, которой не существует
    """

    response = await authenticated_client.get("/vaccines/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Данные о вакцинации не найдены"
