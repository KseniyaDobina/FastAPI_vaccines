from sqlalchemy import select

from models.schemas import VaccineAdd, VaccineID
from models.database import new_session
from models.db_models import VaccineORM

class VaccineRepository:
    # только работает с запросами ну должен
    @classmethod
    async def add_vaccines(cls, vaccine: VaccineAdd):
        async with new_session() as session:
            data = vaccine.model_dump()
            new_vaccine = VaccineORM(**data)
            session.add(new_vaccine)
            await session.flush()
            await session.commit()
            await session.refresh(new_vaccine)
            return new_vaccine

    @classmethod
    async def get_vaccines(cls) -> list[VaccineID]:
        async with new_session() as session:
            query = select(VaccineORM)
            result = await session.execute(query)
            vaccine_models = result.scalars().all()
            vaccines = [VaccineID.model_validate(vaccine_model) for vaccine_model in vaccine_models]
            return vaccines


class VaccineService:
    # делает commit ну должен
    pass
