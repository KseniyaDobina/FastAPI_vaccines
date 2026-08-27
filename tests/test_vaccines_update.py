import pytest
from sqlalchemy import select

from app_vaccines.models.db_models import VaccineBase
from tests.config import client, test_db, authenticated_client
from tests.conftest import vaccine_in_db, vaccine_test_new_data

@pytest.mark.asyncio
async def test_put_vaccine(authenticated_client, vaccine_in_db, test_db, vaccine_test_new_data):
    """
    Обновление существующей вакцинации
    """

    vaccine_id = vaccine_in_db.id
    response = await authenticated_client.put(f"/vaccines/{vaccine_id}",json=vaccine_test_new_data)

    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert "vaccine" in data
    assert data["vaccine"]["id"] == vaccine_id
    assert data["vaccine"]["disease"] == "Грипп"
    assert data["vaccine"]["vaccine_name"] == "Vaxigrip Tetra"
    assert data["vaccine"]["dose_number"] == "1"
    assert data["vaccine"]["vaccination_date"] == "2026-09-15"
    assert data["vaccine"]["expiration_date"] == "2027-06-30"
    assert data["vaccine"]["type_vaccine"] == "Инактивированная, квадривалентная"
    assert data["vaccine"]["lot"] == "VXT2026A91"
    assert data["vaccine"]["manufacturer"] == "Sanofi"
    assert data["vaccine"]["clinic"] == "Frankfurt Medical Center"
    assert data["vaccine"]["country"] == "Germany"
    assert data["vaccine"]["city"] == "Frankfurt am Main"
    assert data["vaccine"]["notes"] == "Сезонная вакцинация против гриппа"

    # Проверяем, что данные действительно изменились в БД
    result = await test_db.execute(
        select(VaccineBase).where(VaccineBase.id == vaccine_id)
    )
    updated_vaccine = result.scalar_one()

    assert updated_vaccine.disease == "Грипп"
    assert updated_vaccine.vaccine_name == "Vaxigrip Tetra"
    assert updated_vaccine.dose_number == "1"
    assert updated_vaccine.vaccination_date.isoformat() == "2026-09-15"
    assert updated_vaccine.expiration_date.isoformat() == "2027-06-30"
    assert updated_vaccine.type_vaccine == "Инактивированная, квадривалентная"
    assert updated_vaccine.lot == "VXT2026A91"
    assert updated_vaccine.manufacturer == "Sanofi"
    assert updated_vaccine.clinic == "Frankfurt Medical Center"
    assert updated_vaccine.country == "Germany"
    assert updated_vaccine.city == "Frankfurt am Main"
    assert updated_vaccine.notes == "Сезонная вакцинация против гриппа"

@pytest.mark.asyncio
async def test_put_vaccine_not_found(authenticated_client, vaccine_test_new_data):
    """
    Обновление вакцинации, которой не существует
    """

    response = await authenticated_client.put("/vaccines/999999", json=vaccine_test_new_data)

    assert response.status_code == 404
    assert response.json()["detail"] == "Данные о вакцинации не найдены"

@pytest.mark.asyncio
async def test_patch_vaccine(authenticated_client, vaccine_in_db, test_db):
    """
        Частичное обновление существующей вакцинации.
        Проверка, что изменилось только переданное поле.
        """

    response = await authenticated_client.patch(f"/vaccines/{vaccine_in_db.id}", json={"city": "Espoo"})

    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert "vaccine" in data
    assert data["vaccine"]["city"] == "Espoo"
    assert data["vaccine"]["disease"] == vaccine_in_db.disease
    assert data["vaccine"]["vaccine_name"] == vaccine_in_db.vaccine_name
    assert data["vaccine"]["clinic"] == vaccine_in_db.clinic
    assert data["vaccine"]["country"] == vaccine_in_db.country
    assert data["vaccine"]["dose_number"] == vaccine_in_db.dose_number
    assert data["vaccine"]["vaccination_date"] == vaccine_in_db.vaccination_date.isoformat()
    assert data["vaccine"]["expiration_date"] == vaccine_in_db.expiration_date.isoformat()
    assert data["vaccine"]["type_vaccine"] == vaccine_in_db.type_vaccine
    assert data["vaccine"]["lot"] == vaccine_in_db.lot
    assert data["vaccine"]["manufacturer"] == vaccine_in_db.manufacturer
    assert data["vaccine"]["notes"] == vaccine_in_db.notes
    # Проверяем БД.
    result = await test_db.execute(
        select(VaccineBase).where(
            VaccineBase.id == vaccine_in_db.id
        )
    )
    updated_vaccine = result.scalar_one()

    assert updated_vaccine.city == "Espoo"
    assert updated_vaccine.disease == vaccine_in_db.disease
    assert updated_vaccine.vaccine_name == vaccine_in_db.vaccine_name
    assert updated_vaccine.dose_number == vaccine_in_db.dose_number
    assert updated_vaccine.vaccination_date == vaccine_in_db.vaccination_date
    assert updated_vaccine.expiration_date == vaccine_in_db.expiration_date
    assert updated_vaccine.type_vaccine == vaccine_in_db.type_vaccine
    assert updated_vaccine.lot == vaccine_in_db.lot
    assert updated_vaccine.manufacturer == vaccine_in_db.manufacturer
    assert updated_vaccine.clinic == vaccine_in_db.clinic
    assert updated_vaccine.country == vaccine_in_db.country
    assert updated_vaccine.notes == vaccine_in_db.notes

@pytest.mark.asyncio
async def test_patch_vaccine_multiple_fields(authenticated_client, vaccine_in_db):
    """
    Проверка частичное обновление нескольких полей.
    """

    vaccine_id = vaccine_in_db.id
    response = await authenticated_client.patch(
        f"/vaccines/{vaccine_id}",
        json={
            "city": "Espoo",
            "clinic": "New Clinic",
        },
    )

    assert response.status_code == 200

    data = response.json()

    # Измененные поля
    assert data["vaccine"]["city"] == "Espoo"
    assert data["vaccine"]["clinic"] == "New Clinic"
    # Неизмененные поля
    assert data["vaccine"]["disease"] == vaccine_in_db.disease
    assert data["vaccine"]["vaccine_name"] == vaccine_in_db.vaccine_name
    assert data["vaccine"]["dose_number"] == vaccine_in_db.dose_number
    assert data["vaccine"]["vaccination_date"] == (vaccine_in_db.vaccination_date.isoformat())
    assert data["vaccine"]["expiration_date"] == (vaccine_in_db.expiration_date.isoformat())
    assert data["vaccine"]["type_vaccine"] == vaccine_in_db.type_vaccine
    assert data["vaccine"]["lot"] == vaccine_in_db.lot
    assert data["vaccine"]["manufacturer"] == vaccine_in_db.manufacturer
    assert data["vaccine"]["country"] == vaccine_in_db.country
    assert data["vaccine"]["notes"] == vaccine_in_db.notes

@pytest.mark.asyncio
async def test_patch_vaccine_not_found(authenticated_client):
    response = await authenticated_client.patch(
        "/vaccines/999999",
        json={
            "city": "Espoo"
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Данные о вакцинации не найдены"
