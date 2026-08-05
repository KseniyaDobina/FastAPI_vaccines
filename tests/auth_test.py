import pytest
from config import settings
import pytest_asyncio

from fastapi import FastAPI, Depends
from httpx import AsyncClient, ASGITransport

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase

from app_vaccines.main import app

client = TestClient(app)



@pytest.fixture
def db():
    await session = TestingSessionLocal()

    yield session

    session.close()

test_engine = create_async_engine(
    "sqlite:///test.db",
    connect_args={"check_same_thread": False}
)

SessionLocal = async_sessionmaker(bind=test_engine)

Base = declarative_base()

async def create_test_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
async def delete_test_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

TestingSessionLocal = async_sessionmaker(bind=test_engine)

def test_get_all_vaccines():
    """
    Тест на получение списка всех записей о вакцинации
    """
    response = client.get('http://127.0.0.1:8000/vaccines')
    assert response.status_code == 200


def test_post_without_data():
    """
    Проверка на проверку входных данных
    """
    response = client.post('http://127.0.0.1:8000/vaccines')
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

def test_post_create_vaccine(vaccine_data):
    """
    Проверка на проверку входных данных
    """
    new_data = {"disease": "tц",
                "vaccine_name": "eц",
                "clinic": "sк",
                "country": "tе",
                "city": "1н"}
    response = client.post('http://127.0.0.1:8000/vaccines', json=vaccine_data)
    assert response.status_code == 201
