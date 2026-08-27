import pytest

from .config import client, test_db, authenticated_client
from tests.conftest import vaccine_test_json_data

@pytest.mark.asyncio
async def test_post_without_data(authenticated_client):
    """
    Проверка валидации входных данных
    """

    response = await authenticated_client.post("/vaccines")

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_post_create_vaccine(authenticated_client, vaccine_test_json_data):
    """
    Проверка создания записи о вакцинации
    """

    response = await authenticated_client.post(
        "/vaccines",
        json=vaccine_test_json_data,
    )
    data = response.json()

    assert "message" in data
    assert "vaccine" in data
    assert isinstance(data["message"], str)
    assert response.status_code == 201

    vaccine = data["vaccine"]

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
async def test_post_create_vaccine_without_notes(authenticated_client, vaccine_test_json_data):
    """
    Проверка создания вакцинации без notes.
    """

    vaccine_test_json_data.pop("notes")
    response = await authenticated_client.post(
        "/vaccines",
        json=vaccine_test_json_data,
    )

    assert response.status_code == 201
    data = response.json()

    assert "vaccine" in data
    assert data["vaccine"]["notes"] is None

@pytest.mark.asyncio
async def test_post_create_vaccine_without_expiration_date(authenticated_client,vaccine_test_json_data):
    """
    Проверка создание вакцинации без expiration_date
    """

    vaccine_test_json_data["expiration_date"] = None
    response = await authenticated_client.post(
        "/vaccines",
        json=vaccine_test_json_data,
    )

    assert response.status_code == 201

    data = response.json()
    assert data["vaccine"]["expiration_date"] is None
