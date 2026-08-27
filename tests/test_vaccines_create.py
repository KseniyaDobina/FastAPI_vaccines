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

@pytest.mark.parametrize(
    "field,value",
    [
        ("disease", "ab"),
        ("vaccine_name", "ab"),
        ("dose_number", ""),
        ("type_vaccine", ""),
        ("lot", ""),
        ("manufacturer", "a"),
        ("clinic", "ab"),
        ("country", "a"),
        ("city", "a"),
    ],
)
@pytest.mark.asyncio
async def test_create_vaccine_min_length_validation(
        authenticated_client,
        vaccine_test_json_data,
        field,
        value
):

    data = vaccine_test_json_data.copy()
    data[field] = value
    response = await authenticated_client.post("/vaccines", json=data)

    assert response.status_code == 422

@pytest.mark.parametrize(
    "field,length",
    [
        ("disease", 101),
        ("vaccine_name", 101),
        ("dose_number", 31),
        ("type_vaccine", 101),
        ("lot", 101),
        ("manufacturer", 101),
        ("clinic", 201),
        ("country", 101),
        ("city", 101),
        ("notes", 301),
    ]
)
@pytest.mark.asyncio
async def test_create_vaccine_max_length_validation(
    authenticated_client,
    vaccine_test_json_data,
    field,
    length
):
    data = vaccine_test_json_data.copy()
    data[field] = "a" * length

    response = await authenticated_client.post("/vaccines", json=data)

    assert response.status_code == 422

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

@pytest.mark.parametrize(
    "field,value",
    [
        ("vaccination_date", "not-a-date"),
        ("vaccination_date", "20.08.2026"),
        ("vaccination_date", "2026/08/20"),
        ("expiration_date", "not-a-date"),
        ("expiration_date", "31.01.2027")
    ]
)
@pytest.mark.asyncio
async def test_create_vaccine_invalid_date(
    authenticated_client,
    vaccine_test_json_data,
    field,
    value
):

    data = vaccine_test_json_data.copy()
    data[field] = value

    response = await authenticated_client.post("/vaccines", json=data )

    assert response.status_code == 422

@pytest.mark.parametrize(
    "field",
    [
        "disease",
        "vaccine_name",
        "dose_number",
        "vaccination_date",
        "type_vaccine",
        "lot",
        "manufacturer",
        "clinic",
        "country",
        "city"
    ]
)
@pytest.mark.asyncio
async def test_create_vaccine_required_fields(
    authenticated_client,
    vaccine_test_json_data,
    field
):

    data = vaccine_test_json_data.copy()
    data.pop(field)

    response = await authenticated_client.post("/vaccines",json=data)

    assert response.status_code == 422

@pytest.mark.parametrize(
    "field",
    [
        "disease",
        "vaccine_name",
        "dose_number",
        "vaccination_date",
        "type_vaccine",
        "lot",
        "manufacturer",
        "clinic",
        "country",
        "city"
    ]
)
@pytest.mark.asyncio
async def test_create_vaccine_none_for_required_fields(
    authenticated_client,
    vaccine_test_json_data,
    field
):
    data = vaccine_test_json_data.copy()
    data[field] = None

    response = await authenticated_client.post("/vaccines", json=data)

    assert response.status_code == 422

    errors = response.json()["detail"]
    assert any(error["loc"][-1] == field for error in errors)
