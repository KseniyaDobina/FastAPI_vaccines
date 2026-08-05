from sqlalchemy import select, update, delete

from models.schemas import VaccineCreate, VaccineID
from models.database import new_session
from models.db_models import VaccineBase

class VaccineRepository:
    """
    Класс для получения информации о вакцинах
    """
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
    """
    Класс для добавления, изменения или удаления вакцин
    """
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
    async def update_vaccine(cls, vaccine_id: int, vaccine: VaccineCreate):
        async with new_session() as session:
            query = update(VaccineBase).where(VaccineBase.id == vaccine_id).values(**vaccine.model_dump())
            await session.execute(query)
            await session.commit()
            result = await session.execute(
                select(VaccineBase).where(VaccineBase.id == vaccine_id)
            )
            updated_db_model = result.scalar_one_or_none()
            return VaccineID.model_validate(updated_db_model)

    @classmethod
    async def delete_vaccine(cls, vaccine_id: int) -> bool:
        async with new_session() as session:
            query = delete(VaccineBase).where(VaccineBase.id == vaccine_id)
            result = await session.execute(query)
            await session.commit()
            # result.rowcount показывает, сколько строк было затронуто (0 или 1)
            return result.rowcount > 0
