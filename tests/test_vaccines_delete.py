import pytest
from sqlalchemy import select

from app_vaccines.models.db_models import Vaccine
from tests.config import client, test_db, authenticated_client, test_user
from tests.conftest import vaccine_in_db

@pytest.mark.asyncio
async def test_delete_vaccine(authenticated_client, vaccine_in_db, test_db):
    """
    Удаление существующей вакцинации
    """

    vaccine_id = vaccine_in_db.id
    response = await authenticated_client.delete(f"/vaccines/{vaccine_id}")

    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert data["message"] == f"Удалена вакцина №{vaccine_id}"
    # Проверяем, что запись действительно удалена
    result = await test_db.execute(
        select(Vaccine).where(
            Vaccine.id == vaccine_id
        )
    )
    deleted_vaccine = result.scalar_one_or_none()

    assert deleted_vaccine is None

@pytest.mark.asyncio
async def test_delete_vaccine_not_found(authenticated_client):
    """
    Удаление вакцинации, которой не существует
    """

    response = await authenticated_client.delete(
        "/vaccines/999999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Данные о вакцинации не найдены"
