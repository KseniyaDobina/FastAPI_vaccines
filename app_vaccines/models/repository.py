from sqlalchemy import select

from models.schemas import VaccineAdd, VaccineID
from models.database import new_session
from models.db_models import VaccineBase

class VaccineRepository:
    # только работает с запросами ну должен
    @classmethod
    async def add_vaccines(cls, vaccine: VaccineAdd):
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
    async def get_vaccine_id(cls, vaccine_id: int) -> VaccineID:
        async with new_session() as session:
            query = select(VaccineBase).where(VaccineBase.id == vaccine_id)
            result = await session.execute(query)
            vaccine = result.scalars().first()
            return vaccine


class VaccineService:
    # делает commit ну должен
    pass
