from sqlalchemy import select, update

from models.schemas import VaccineCreate, VaccineID, VaccineUpdate
from models.database import new_session
from models.db_models import VaccineBase

class VaccineRepository:
    # только работает с запросами ну должен
    @classmethod
    async def add_vaccines(cls, vaccine: VaccineCreate):
        async with new_session() as session:
            data = vaccine.model_dump()
            new_vaccine = VaccineBase(**data)
            session.add(new_vaccine)
            await session.flush()
            await session.commit()
            await session.refresh(new_vaccine)
            return new_vaccine

    @classmethod
    async def get_vaccines(cls) -> list[VaccineID]:
        async with new_session() as session:
            query = select(VaccineBase)
            result = await session.execute(query)
            vaccine_models = result.scalars().all()
            vaccines = [VaccineID.model_validate(vaccine_model) for vaccine_model in vaccine_models]
            return vaccines

    @classmethod
    async def get_vaccine_by_id(cls, vaccine_id: int):
        async with new_session() as session:
            query = select(VaccineBase).where(VaccineBase.id == vaccine_id)
            result = await session.execute(query)
            vaccine = result.scalar_one_or_none()
            if vaccine is None:
                return False
            return VaccineID.model_validate(vaccine)


class VaccineService:
    # делает commit ну должен
    @classmethod
    async def update_vaccine(cls, vaccine_id:int, vaccine: VaccineCreate):
        async with new_session() as session:
            query = select(VaccineBase).where(VaccineBase.id == vaccine_id)
            result = await session.execute(query)
            vaccine_db = result.scalar_one_or_none()
            if vaccine_db is None:
                return False
            query = update(VaccineBase).where(VaccineBase.id == vaccine_id).values(**vaccine.model_dump())
            result = await session.execute(query)
            await session.commit()
            await session.refresh(vaccine_db)
            return vaccine_db

