import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Дефолтные значения для локального запуска тестов, если .env не настроен.
# setdefault() ничего не перезапишет, если переменная уже задана - ни через
# реальный .env локально, ни через env в CI (.github/workflows/tests.yml)
os.environ.setdefault("PATH_TO_DB", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("KEYCLOAK_URL", "http://localhost:8080")
os.environ.setdefault("KEYCLOAK_REALM", "test-realm")
os.environ.setdefault("KEYCLOAK_CLIENT_ID", "test-client")

# Тестовая бд
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)
