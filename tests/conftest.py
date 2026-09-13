from datetime import date

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app_vaccines.auth.dependencies import get_current_user
from app_vaccines.main import app
from app_vaccines.models.database import Base, get_session
from app_vaccines.models.db_models import User, Vaccine
from app_vaccines.models.schemas import CurrentUser
from tests.config import TestingSessionLocal, test_engine


@pytest_asyncio.fixture
async def test_db():
    """Полностью изолированная БД на один тест."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

        try:
            async with TestingSessionLocal() as session:
                yield session

        finally:
            async with test_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)


# HTTP CLIENT

@pytest_asyncio.fixture
async def client(test_db):
    """Неавторизованный HTTP client."""
    async def override_get_db():
        yield test_db

    old_db_override = app.dependency_overrides.get(get_session)
    # ВАЖНО:
    # здесь должен быть импорт именно той функции,
    # которую FastAPI использует как Depends для получения БД.

    # говорим FastAPI:
    # вместо настоящего get_session использовать тестовый
    app.dependency_overrides[get_session] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", ) as http_client:
            yield http_client
    finally:
        if old_db_override is None:
            app.dependency_overrides.pop(get_session, None)
        else:
            app.dependency_overrides[get_session] = old_db_override


@pytest_asyncio.fixture
async def test_user(test_db):
    user = User(
        keycloak_id="test-keycloak-id",
        username="test_user",
        email="test@example.com",
    )

    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    return user


@pytest_asyncio.fixture
async def authenticated_client(client, test_user):
    async def override_get_current_user():
        return CurrentUser(
            sub="test-keycloak-id",
            username="test_user",
            email="test@example.com",
        )

    old_user_override = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = override_get_current_user
    try:
        yield client
    finally:
        if old_user_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = old_user_override


@pytest_asyncio.fixture
async def second_user(test_db):
    user = User(
        keycloak_id="second-keycloak-id",
        username="second_user",
        email="second@example.com",
    )

    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    return user


@pytest_asyncio.fixture
async def second_user_vaccine(
        test_db,
        second_user,
        vaccine_test_data,
):
    vaccine = Vaccine(**vaccine_test_data, user_id=second_user.id)

    test_db.add(vaccine)
    await test_db.commit()
    await test_db.refresh(vaccine)

    return vaccine


@pytest_asyncio.fixture
async def authenticated_client_new_user(client):
    """HTTP client с валидным (замоканным) токеном для пользователя,
    которого ЕЩЁ НЕТ в БД - имитирует первый визит после логина в Keycloak.
    """
    async def override_get_current_user():
        return CurrentUser(
            sub="brand-new-keycloak-id",
            username="brand_new_user",
            email="brand_new@example.com",
        )

    old_user_override = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = override_get_current_user
    try:
        yield client
    finally:
        if old_user_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = old_user_override



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
async def vaccine_test(vaccine_test_data, test_user):
    return Vaccine(**vaccine_test_data, user_id=test_user.id)


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
