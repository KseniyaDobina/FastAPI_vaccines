from datetime import datetime

# Подключение БД
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from models.schemas import VaccineAdd, VaccineID

engine = create_async_engine('sqlite+aiosqlite:///vaccines_db.sqlite3')
new_session = async_sessionmaker(engine, expire_on_commit=False)

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class BaseModel(DeclarativeBase):
    pass

class VaccineORM(BaseModel):
    __tablename__ = 'vaccines'
    id: Mapped[int] = mapped_column(primary_key=True)
    disease: Mapped[str]
    vaccine_name: Mapped[str]
    # vaccination_date: Mapped[datetime]
    # expiration_date: Mapped[datetime | None]
    clinic: Mapped[str]
    country: Mapped[str]
    city: Mapped[str]
    notes: Mapped[str | None]


class VaccineRepository:
    @classmethod
    async def add_vaccines(cls, vaccine: VaccineAdd):
        async with new_session() as session:
            data = vaccine.model_dump()
            new_vaccine = VaccineORM(**data)
            session.add(new_vaccine)
            await session.flush()
            await session.commit()
            return new_vaccine

    @classmethod
    async def get_vaccines(cls) -> list[VaccineID]:
        async with new_session() as session:
            query = select(VaccineORM)
            result = await session.execute(query)
            vaccine_models = result.scalars().all()
            vaccines = [VaccineID.model_validate(vaccine_model) for vaccine_model in vaccine_models]
            return vaccines

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
