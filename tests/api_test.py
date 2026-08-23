import pytest
from sqlalchemy import select

from app_vaccines.models.db_models import VaccineBase
from tests.config import client, test_db
from tests.conftest import vaccine_test_data, vaccine_test, vaccine_in_db

# @pytest.fixture
# async def vaccine_test_db(session, vaccine_test):
#     session.add(vaccine_test)
#     await session.commit()
#     await session.refresh(vaccine_test)
#     return vaccine_test

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
async def test_post_without_data(client):
    """
    Проверка валидации входных данных
    """

    response = await client.post("/vaccines")

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_post_create_vaccine(client, vaccine_test_data):
    """
    Проверка создания записи о вакцинации
    """

    response = await client.post(
        "/vaccines",
        json=vaccine_test_data,
    )
    data = response.json()

    assert "message" in data
    assert "vaccine" in data
    assert isinstance(data["message"], str)
    assert response.status_code == 201

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
    assert data["message"] == f"Информация о вакцине №{vaccine_in_db.id}"
    assert data["vaccine"]["id"] == vaccine_in_db.id
    assert data["vaccine"]["disease"] == "COVID-19"
    assert data["vaccine"]["vaccine_name"] == "Sputnik V"

@pytest.mark.asyncio
async def test_get_vaccine_not_found(client):
    """
    Получение вакцинации, которой не существует
    """

    response = await client.get("/vaccines/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Данные о вакцинации не найдены"

@pytest.mark.asyncio
async def test_put_vaccine(client, vaccine_in_db, test_db):
    """
    Обновление существующей вакцинации
    """

    vaccine_id = vaccine_in_db.id

    # Новые данные
    new_data = {
        "disease": "Грипп",
        "vaccine_name": "Совигрипп",
        "clinic": "Поликлиника №2",
        "country": "Россия",
        "city": "Москва",
    }

    response = await client.put(f"/vaccines/{vaccine_id}",json=new_data)

    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert "vaccine" in data
    assert data["vaccine"]["id"] == vaccine_id
    # Проверяем, что данные действительно изменились в БД
    result = await test_db.execute(
        select(VaccineBase).where(VaccineBase.id == vaccine_id)
    )
    updated_vaccine = result.scalar_one()

    assert updated_vaccine.disease == "Грипп"
    assert updated_vaccine.vaccine_name == "Совигрипп"
    assert updated_vaccine.clinic == "Поликлиника №2"
    assert updated_vaccine.country == "Россия"
    assert updated_vaccine.city == "Москва"

@pytest.mark.asyncio
async def test_put_vaccine_not_found(client):
    """
    Обновление вакцинации, которой не существует
    """

    new_data = {
        "disease": "Грипп",
        "vaccine_name": "Совигрипп",
        "clinic": "Поликлиника №2",
        "country": "Россия",
        "city": "Москва",
    }
    response = await client.put("/vaccines/999999", json=new_data)

    assert response.status_code == 404
    assert response.json()["detail"] == "Данные о вакцинации не найдены"

@pytest.mark.asyncio
async def test_patch_vaccine(client, vaccine_in_db, test_db):
    """
        Частичное обновление существующей вакцинации.
        Проверяем, что изменилось только переданное поле.
        """

    response = await client.patch(f"/vaccines/{vaccine_in_db.id}", json={"city": "Espoo"})

    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert "vaccine" in data
    assert data["vaccine"]["city"] == "Espoo"
    assert data["vaccine"]["disease"] == vaccine_in_db.disease
    assert data["vaccine"]["vaccine_name"] == vaccine_in_db.vaccine_name
    assert data["vaccine"]["clinic"] == vaccine_in_db.clinic
    assert data["vaccine"]["country"] == vaccine_in_db.country
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
    assert updated_vaccine.clinic == vaccine_in_db.clinic
    assert updated_vaccine.country == vaccine_in_db.country

@pytest.mark.asyncio
async def test_patch_vaccine_multiple_fields(client, vaccine_in_db):
    """
    Проверяем частичное обновление нескольких полей.
    """

    vaccine_id = vaccine_in_db.id
    response = await client.patch(
        f"/vaccines/{vaccine_id}",
        json={
            "city": "Espoo",
            "clinic": "New Clinic",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["vaccine"]["city"] == "Espoo"
    assert data["vaccine"]["clinic"] == "New Clinic"
    # Остальные поля не должны измениться.
    assert data["vaccine"]["disease"] == vaccine_in_db.disease
    assert data["vaccine"]["vaccine_name"] == vaccine_in_db.vaccine_name
    assert data["vaccine"]["country"] == vaccine_in_db.country

@pytest.mark.asyncio
async def test_patch_vaccine_not_found(client):
    response = await client.patch(
        "/vaccines/999999",
        json={
            "city": "Espoo"
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Данные о вакцинации не найдены"

@pytest.mark.asyncio
async def test_delete_vaccine(client, vaccine_in_db, test_db):
    """
    Удаление существующей вакцинации
    """

    vaccine_id = vaccine_in_db.id
    response = await client.delete(f"/vaccines/{vaccine_id}")

    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert data["message"] == f"Удалена вакцина №{vaccine_id}"
    # Проверяем, что запись действительно удалена
    result = await test_db.execute(
        select(VaccineBase).where(
            VaccineBase.id == vaccine_id
        )
    )
    deleted_vaccine = result.scalar_one_or_none()

    assert deleted_vaccine is None

@pytest.mark.asyncio
async def test_delete_vaccine_not_found(client):
    """
    Удаление вакцинации, которой не существует
    """

    response = await client.delete(
        "/vaccines/999999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Данные о вакцинации не найдены"
