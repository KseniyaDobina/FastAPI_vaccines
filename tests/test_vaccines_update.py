import pytest
from sqlalchemy import select

from app_vaccines.models.db_models import Vaccine
from tests.config import client, test_db, authenticated_client, test_user
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
    assert data["id"] == vaccine_id
    assert data["disease"] == "Грипп"
    assert data["vaccine_name"] == "Vaxigrip Tetra"
    assert data["dose_number"] == "1"
    assert data["vaccination_date"] == "2026-09-15"
    assert data["expiration_date"] == "2027-06-30"
    assert data["type_vaccine"] == "Инактивированная, квадривалентная"
    assert data["lot"] == "VXT2026A91"
    assert data["manufacturer"] == "Sanofi"
    assert data["clinic"] == "Frankfurt Medical Center"
    assert data["country"] == "Germany"
    assert data["city"] == "Frankfurt am Main"
    assert data["notes"] == "Сезонная вакцинация против гриппа"

    # Проверяем, что данные действительно изменились в БД
    result = await test_db.execute(
        select(Vaccine).where(Vaccine.id == vaccine_id)
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
    assert data["id"] == vaccine_in_db.id
    assert data["vaccine_name"] == vaccine_test_new_data["vaccine_name"]
    assert data["manufacturer"] == vaccine_test_new_data["manufacturer"]
    assert data["clinic"] == vaccine_test_new_data["clinic"]

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
    assert data["city"] == "Espoo"
    assert data["disease"] == vaccine_in_db.disease
    assert data["vaccine_name"] == vaccine_in_db.vaccine_name
    assert data["clinic"] == vaccine_in_db.clinic
    assert data["country"] == vaccine_in_db.country
    assert data["dose_number"] == vaccine_in_db.dose_number
    assert data["vaccination_date"] == vaccine_in_db.vaccination_date.isoformat()
    assert data["expiration_date"] == vaccine_in_db.expiration_date.isoformat()
    assert data["type_vaccine"] == vaccine_in_db.type_vaccine
    assert data["lot"] == vaccine_in_db.lot
    assert data["manufacturer"] == vaccine_in_db.manufacturer
    assert data["notes"] == vaccine_in_db.notes
    # Проверяем БД.
    result = await test_db.execute(
        select(Vaccine).where(
            Vaccine.id == vaccine_in_db.id
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
    assert data["city"] == "Espoo"
    assert data["clinic"] == "New Clinic"
    # Неизмененные поля
    assert data["disease"] == vaccine_in_db.disease
    assert data["vaccine_name"] == vaccine_in_db.vaccine_name
    assert data["dose_number"] == vaccine_in_db.dose_number
    assert data["vaccination_date"] == (vaccine_in_db.vaccination_date.isoformat())
    assert data["expiration_date"] == (vaccine_in_db.expiration_date.isoformat())
    assert data["type_vaccine"] == vaccine_in_db.type_vaccine
    assert data["lot"] == vaccine_in_db.lot
    assert data["manufacturer"] == vaccine_in_db.manufacturer
    assert data["country"] == vaccine_in_db.country
    assert data["notes"] == vaccine_in_db.notes

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

@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("disease", "ab"),           # min=3
        ("vaccine_name", "ab"),      # min=3
        ("dose_number", ""),         # min=1
        ("type_vaccine", ""),        # min=1
        ("lot", ""),                 # min=1
        ("manufacturer", "a"),       # min=2
        ("clinic", "ab"),            # min=3
        ("country", "a"),            # min=2
        ("city", "a"),               # min=2
        ("notes", ""),               # min=1
    ],
)
@pytest.mark.asyncio
async def test_patch_rejects_too_short_string_fields(
    authenticated_client,
    vaccine_in_db,
    field,
    value,
):
    response = await authenticated_client.patch(f"/vaccines/{vaccine_in_db.id}", json={field: value})

    assert response.status_code == 422

    errors = response.json()["detail"]
    assert any(error["loc"][-1] == field for error in errors)

@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("disease", "a" * 101),
        ("vaccine_name", "a" * 101),
        ("dose_number", "a" * 31),
        ("type_vaccine", "a" * 101),
        ("lot", "a" * 101),
        ("manufacturer", "a" * 101),
        ("clinic", "a" * 201),
        ("country", "a" * 101),
        ("city", "a" * 101),
        ("notes", "a" * 301),
    ],
)
@pytest.mark.asyncio
async def test_patch_rejects_too_long_string_fields(
    authenticated_client,
    vaccine_in_db,
    field,
    value,
):
    response = await authenticated_client.patch(f"/vaccines/{vaccine_in_db.id}", json={field: value})

    assert response.status_code == 422

    errors = response.json()["detail"]
    assert any(error["loc"][-1] == field for error in errors)

@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("disease", "abc"),                  # 3
        ("vaccine_name", "abc"),             # 3
        ("dose_number", "1"),                # 1
        ("type_vaccine", "a"),               # 1
        ("lot", "a"),                        # 1
        ("manufacturer", "ab"),              # 2
        ("clinic", "abc"),                   # 3
        ("country", "ab"),                   # 2
        ("city", "ab"),                      # 2
        ("notes", "a"),                      # 1
    ],
)
@pytest.mark.asyncio
async def test_patch_accepts_minimum_string_lengths(
    authenticated_client,
    vaccine_in_db,
    field,
    value,
):
    response = await authenticated_client.patch(f"/vaccines/{vaccine_in_db.id}", json={field: value})

    assert response.status_code == 200
    assert response.json()[field] == value

@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("disease", "a" * 100),
        ("vaccine_name", "a" * 100),
        ("dose_number", "a" * 30),
        ("type_vaccine", "a" * 100),
        ("lot", "a" * 100),
        ("manufacturer", "a" * 100),
        ("clinic", "a" * 200),
        ("country", "a" * 100),
        ("city", "a" * 100),
        ("notes", "a" * 300),
    ],
)
@pytest.mark.asyncio
async def test_patch_accepts_maximum_string_lengths(
    authenticated_client,
    vaccine_in_db,
    field,
    value,
):
    response = await authenticated_client.patch(f"/vaccines/{vaccine_in_db.id}", json={field: value})

    assert response.status_code == 200
    assert response.json()[field] == value

@pytest.mark.parametrize(
    "field",
    ["vaccination_date", "expiration_date"],
)
@pytest.mark.asyncio
async def test_patch_rejects_invalid_date_format(
    authenticated_client,
    vaccine_in_db,
    field,
):
    response = await authenticated_client.patch(f"/vaccines/{vaccine_in_db.id}", json={field: "not-a-date"})

    assert response.status_code == 422

    errors = response.json()["detail"]
    assert any(error["loc"][-1] == field for error in errors)

@pytest.mark.asyncio
async def test_patch_rejects_expiration_date_before_vaccination_date(
    authenticated_client,
    vaccine_in_db,
):
    response = await authenticated_client.patch(
        f"/vaccines/{vaccine_in_db.id}",
        json={"vaccination_date": "2026-08-20", "expiration_date": "2026-08-19"}
    )

    assert response.status_code == 422

    assert any(
        "expiration_date должна быть позже, чем vaccination_date"
        in error["msg"]
        for error in response.json()["detail"]
    )

@pytest.mark.asyncio
async def test_patch_rejects_equal_vaccination_and_expiration_dates(
    authenticated_client,
    vaccine_in_db,
):
    response = await authenticated_client.patch(
        f"/vaccines/{vaccine_in_db.id}",
        json={"vaccination_date": "2026-08-20", "expiration_date": "2026-08-20"})

    assert response.status_code == 422

    assert any(
        "expiration_date должна быть позже, чем vaccination_date"
        in error["msg"]
        for error in response.json()["detail"]
    )

@pytest.mark.asyncio
async def test_patch_accepts_valid_dates(
    authenticated_client,
    vaccine_in_db,
):
    response = await authenticated_client.patch(
        f"/vaccines/{vaccine_in_db.id}",
        json={
            "vaccination_date": "2026-08-20", "expiration_date": "2027-08-20"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["vaccination_date"] == "2026-08-20"
    assert data["expiration_date"] == "2027-08-20"