import pytest_asyncio

from httpx2 import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from app_vaccines.main import app
from app_vaccines.models.database import Base, get_session

# ВАЖНО:
# здесь должен быть импорт именно той функции,
# которую FastAPI использует как Depends для получения БД.
#
# Например:


# ==========================================
# ТЕСТОВАЯ БД
# ==========================================

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ==========================================
# СОЗДАНИЕ / УДАЛЕНИЕ ТАБЛИЦ
# ==========================================

@pytest_asyncio.fixture(scope="function")
async def test_db():
    # создаём таблицы перед тестом
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # создаём сессию
    async with TestingSessionLocal() as session:
        yield session

    # после теста удаляем таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ==========================================
# HTTP CLIENT
# ==========================================

@pytest_asyncio.fixture
async def client(test_db):

    async def override_get_db():
        yield test_db

    # говорим FastAPI:
    # вместо настоящего get_db использовать тестовый
    app.dependency_overrides[get_session] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    # обязательно очищаем override
    app.dependency_overrides.clear()

import pytest


@pytest.mark.asyncio
async def test_get_all_vaccines(client):
    """
    Тест на получение списка всех записей о вакцинации.
    """

    response = await client.get("/vaccines")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_without_data(client):
    """
    Проверка валидации входных данных.
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
    Проверка создания записи о вакцинации.
    """

    response = await client.post(
        "/vaccines",
        json=vaccine_data,
    )

    assert response.status_code == 201


# import pytest
# from config import settings
# import pytest_asyncio
#
# from fastapi import FastAPI, Depends
# from httpx import AsyncClient, ASGITransport
#
# from sqlalchemy import Column, Integer, String
# from sqlalchemy.ext.asyncio import (
#     create_async_engine,
#     AsyncSession,
#     async_sessionmaker
# )
# from sqlalchemy.orm import DeclarativeBase
#
# from app_vaccines.main import app
#
# client = TestClient(app)
#
#
#
# @pytest.fixture
# def db():
#     await session = TestingSessionLocal()
#
#     yield session
#
#     session.close()
#
# test_engine = create_async_engine(
#     "sqlite:///test.db",
#     connect_args={"check_same_thread": False}
# )
#
# SessionLocal = async_sessionmaker(bind=test_engine)
#
# Base = declarative_base()
#
# async def create_test_database():
#     async with test_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
# async def delete_test_database():
#     async with test_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#
# TestingSessionLocal = async_sessionmaker(bind=test_engine)
#
# def test_get_all_vaccines():
#     """
#     Тест на получение списка всех записей о вакцинации
#     """
#     response = client.get('http://127.0.0.1:8000/vaccines')
#     assert response.status_code == 200
#
#
# def test_post_without_data():
#     """
#     Проверка на проверку входных данных
#     """
#     response = client.post('http://127.0.0.1:8000/vaccines')
#     assert response.status_code == 422
#
# @pytest.fixture
# def vaccine_data():
#     return {
#         "disease": "COVID-19",
#         "vaccine_name": "Sputnik V",
#         "clinic": "Поликлиника №1",
#         "country": "Россия",
#         "city": "Москва",
#     }
#
# def test_post_create_vaccine(vaccine_data):
#     """
#     Проверка на проверку входных данных
#     """
#     new_data = {"disease": "tц",
#                 "vaccine_name": "eц",
#                 "clinic": "sк",
#                 "country": "tе",
#                 "city": "1н"}
#     response = client.post('http://127.0.0.1:8000/vaccines', json=vaccine_data)
#     assert response.status_code == 201
