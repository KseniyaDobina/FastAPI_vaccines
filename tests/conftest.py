from datetime import date
import pytest_asyncio

from app_vaccines.models.db_models import VaccineBase

@pytest_asyncio.fixture
async def vaccine_test_data():
    return {
        "disease": "COVID-19",
        "vaccine_name": "Comirnaty",
        "dose_number": "1",
        "vaccination_date": date(2026, 8, 20),
        "expiration_date": date(2027, 1, 31),
        "type_vaccine": "mRNA",
        "lot": "ABC12345",
        "manufacturer": "Pfizer-BioNTech",
        "clinic": "City Medical Center",
        "country": "Germany",
        "city": "Frankfurt am Main",
        "notes": "Вакцинация проведена без осложнений"
    }

@pytest_asyncio.fixture
async def vaccine_test(vaccine_test_data):
    return VaccineBase(**vaccine_test_data)

@pytest_asyncio.fixture
async def vaccine_in_db(test_db, vaccine_test):
    test_db.add(vaccine_test)
    await test_db.commit()
    await test_db.refresh(vaccine_test)
    return vaccine_test

@pytest_asyncio.fixture
async def vaccine_test_json_data(vaccine_test_data):
    return {
        **vaccine_test_data,
        "vaccination_date": vaccine_test_data["vaccination_date"].isoformat(),
        "expiration_date": vaccine_test_data["expiration_date"].isoformat(),
    }

@pytest_asyncio.fixture
async def vaccine_test_new_data():
    return {
        "disease": "Грипп",
        "vaccine_name": "Vaxigrip Tetra",
        "dose_number": "1",
        "vaccination_date": "2026-09-15",
        "expiration_date": "2027-06-30",
        "type_vaccine": "Инактивированная, квадривалентная",
        "lot": "VXT2026A91",
        "manufacturer": "Sanofi",
        "clinic": "Frankfurt Medical Center",
        "country": "Germany",
        "city": "Frankfurt am Main",
        "notes": "Сезонная вакцинация против гриппа"
    }

# Для тестов с фэйковым пользователем
# app.dependency_overrides[get_current_user] = fake_user
# def fake_user():
#     return {
#         "sub": "test-user-id",
#         "preferred_username": "test-user",
#         "realm_access": {
#             "roles": ["user"]
#         }
#     }
