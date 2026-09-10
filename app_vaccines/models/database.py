from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app_vaccines.config.settings import settings
from app_vaccines.models.db_models import Base

engine = create_async_engine(settings.PATH_TO_DB)
new_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with new_session() as session:
        yield session


async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def delete_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
