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
    assert data["id"] == vaccine_in_db.id


@pytest.mark.asyncio
async def test_get_vaccine_not_found(authenticated_client):
    """
    Получение вакцинации, которой не существует
    """

    response = await authenticated_client.get("/vaccines/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Данные о вакцинации не найдены"


@pytest.mark.asyncio
async def test_get_all_vaccines_default_pagination(authenticated_client):
    """
    Без параметров запрос должен отработать с дефолтными skip=0, limit=10
    """

    response = await authenticated_client.get("/vaccines")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.parametrize("limit", [1, 20])
@pytest.mark.asyncio
async def test_get_all_vaccines_accepts_limit_within_bounds(authenticated_client, limit):
    """
    limit=1 и limit=20 - границы допустимого диапазона, должны приниматься
    """

    response = await authenticated_client.get("/vaccines", params={"limit": limit})

    assert response.status_code == 200


@pytest.mark.parametrize("limit", [-1, 0, 21, 1000])
@pytest.mark.asyncio
async def test_get_all_vaccines_rejects_limit_out_of_bounds(authenticated_client, limit):
    """
    limit=0 и limit>20 должны отклоняться на уровне валидации запроса
    """

    response = await authenticated_client.get("/vaccines", params={"limit": limit})

    assert response.status_code == 422

    errors = response.json()["detail"]
    assert any(error["loc"][-1] == "limit" for error in errors)


@pytest.mark.asyncio
async def test_get_all_vaccines_accepts_skip_zero(authenticated_client):
    """
    skip=0 - граница допустимого диапазона, должен приниматься
    """

    response = await authenticated_client.get("/vaccines", params={"skip": 0})

    assert response.status_code == 200


@pytest.mark.parametrize("skip", [-1, -100])
@pytest.mark.asyncio
async def test_get_all_vaccines_rejects_negative_skip(authenticated_client, skip):
    """
    Отрицательный skip должен отклоняться на уровне валидации запроса
    """

    response = await authenticated_client.get("/vaccines", params={"skip": skip})

    assert response.status_code == 422

    errors = response.json()["detail"]
    assert any(error["loc"][-1] == "skip" for error in errors)
