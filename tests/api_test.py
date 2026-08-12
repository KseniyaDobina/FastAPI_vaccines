import pytest
from sqlalchemy import select

from app_vaccines.models.db_models import VaccineBase
from app_vaccines.models.database import get_session
from tests.config import client, test_db

@pytest.mark.asyncio
async def test_get_all_vaccines(client):
    """
    Тест на получение списка всех записей о вакцинации
    """

    response = await client.get("/vaccines")

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_post_without_data(client):
    """
    Проверка валидации входных данных
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
    Проверка создания записи о вакцинации
    """

    response = await client.post(
        "/vaccines",
        json=vaccine_data,
    )

    assert response.status_code == 201

@pytest.mark.asyncio
async def test_get_vaccine(client, test_db):
    """
    Получение существующей вакцинации по ID
    """

    vaccine = VaccineBase(
        disease="COVID-19",
        vaccine_name="Sputnik V",
        clinic="Поликлиника №1",
        country="Россия",
        city="Москва",
    )

    test_db.add(vaccine)
    await test_db.commit()
    await test_db.refresh(vaccine)

    response = await client.get(
        f"/vaccines/{vaccine.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == f"Информация о вакцине №{vaccine.id}"
    assert data["vaccine"]["id"] == vaccine.id
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
async def test_put_vaccine(client, test_db):
    """
    Обновление существующей вакцинации
    """

    # Создаем исходную запись
    vaccine = VaccineBase(
        disease="COVID-19",
        vaccine_name="Sputnik V",
        clinic="Поликлиника №1",
        country="Россия",
        city="Москва",
    )

    test_db.add(vaccine)
    await test_db.commit()
    await test_db.refresh(vaccine)

    vaccine_id = vaccine.id

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
    assert data["vaccine"]["id"] == 1

    # Проверяем, что данные действительно изменились в БД
    result = await test_db.execute(
        select(VaccineBase).where(VaccineBase.id == vaccine_id)
    )
    updated_vaccine = result.scalar_one()
    print(response.json())
    print(updated_vaccine.disease, 1)

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

    response = await client.put(
        "/vaccines/999999",
        json=new_data,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Данные о вакцинации не найдены"

@pytest.mark.asyncio
async def test_delete_vaccine(client, test_db):
    """
    Удаление существующей вакцинации
    """

    vaccine = VaccineBase(
        disease="COVID-19",
        vaccine_name="Sputnik V",
        clinic="Поликлиника №1",
        country="Россия",
        city="Москва",
    )

    test_db.add(vaccine)
    await test_db.commit()
    await test_db.refresh(vaccine)

    vaccine_id = vaccine.id

    response = await client.delete(
        f"/vaccines/{vaccine_id}"
    )

    assert response.status_code == 200

    data = response.json()

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
