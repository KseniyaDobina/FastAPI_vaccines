import pytest
import pytest_asyncio
from app_vaccines.models.db_models import VaccineBase

@pytest_asyncio.fixture
async def vaccine_test_data():
    return {
        "disease": "COVID-19",
        "vaccine_name": "Sputnik V",
        "clinic": "Поликлиника №1",
        "country": "Россия",
        "city": "Москва",
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
