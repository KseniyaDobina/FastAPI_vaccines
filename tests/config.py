import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app_vaccines.auth.dependencies import get_current_user
from app_vaccines.main import app
from app_vaccines.models.database import Base, get_session
from app_vaccines.models.schemas import CurrentUser

# Тестовая бд
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Создание таблиц, сессия и удаление таблиц"""
    # создаём таблицы перед тестом
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # создаём сессию
    async with TestingSessionLocal() as session:
        yield session

    # после теста удаляем таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# HTTP CLIENT

@pytest_asyncio.fixture
async def client(test_db):

    async def override_get_db():
        yield test_db

    # ВАЖНО:
    # здесь должен быть импорт именно той функции,
    # которую FastAPI использует как Depends для получения БД.

    # говорим FastAPI:
    # вместо настоящего get_session использовать тестовый
    app.dependency_overrides[get_session] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    # очищаем override
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def authenticated_client(client):

    async def override_get_current_user():
        return CurrentUser(
            sub="test-keycloak-id",
            username="test_user",
            email="test@example.com",
        )

    app.dependency_overrides[get_current_user] = (
        override_get_current_user
    )

    yield client
    app.dependency_overrides.clear()

