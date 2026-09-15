from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app_vaccines.config.settings import settings
from app_vaccines.models.db_models import Base

engine = create_async_engine(settings.PATH_TO_DB)
new_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with new_session() as session:
        yield session


async def create_database()  -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def delete_database()  -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
