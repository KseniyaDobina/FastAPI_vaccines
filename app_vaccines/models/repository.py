from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app_vaccines.models.schemas import VaccineCreate, VaccineID, VaccineUpdate
from app_vaccines.models.db_models import VaccineBase

class VaccineRepository:
    """
    Класс для получения информации о вакцинах
    """
    @classmethod
    async def get_vaccines(cls, session: AsyncSession) -> list[VaccineID]:
        query = select(VaccineBase)
        result = await session.execute(query)
        vaccine_models = result.scalars().all()
        vaccines = [VaccineID.model_validate(vaccine_model) for vaccine_model in vaccine_models]
        return vaccines

    @classmethod
    async def get_vaccine_by_id(cls, vaccine_id: int, session: AsyncSession):
        query = select(VaccineBase).where(VaccineBase.id == vaccine_id)
        result = await session.execute(query)
        vaccine = result.scalar_one_or_none()
        if vaccine is None:
            return None
        return VaccineID.model_validate(vaccine)


class VaccineService:
    """
    Класс для добавления, изменения или удаления вакцин
    """
    @classmethod
    async def add_vaccine(cls, vaccine: VaccineCreate, session: AsyncSession):
        data = vaccine.model_dump()
        new_vaccine = VaccineBase(**data)
        session.add(new_vaccine)
        await session.flush()
        await session.commit()
        await session.refresh(new_vaccine)
        return new_vaccine

    @classmethod
    async def update_vaccine(cls, vaccine_id: int, vaccine: VaccineCreate, session: AsyncSession):
        query = update(VaccineBase).where(VaccineBase.id == vaccine_id).values(**vaccine.model_dump())
        result = await session.execute(query)
        if result.rowcount == 0:
            await session.rollback()
            return None

        await session.commit()
        result = await session.execute(
            select(VaccineBase).where(VaccineBase.id == vaccine_id)
        )
        updated_db_model = result.scalar_one_or_none()
        if updated_db_model is None:
            return None
        return VaccineID.model_validate(updated_db_model)

    @classmethod
    async def update_vaccine_patch(cls, vaccine_id: int, vaccine: VaccineUpdate, session: AsyncSession):
        query = select(VaccineBase).where(VaccineBase.id == vaccine_id)
        result = await session.execute(query)
        vaccine_db = result.scalar_one_or_none()
        if vaccine_db is None:
            return None

        update_data = vaccine.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vaccine_db, field, value)

        await session.commit()
        await session.refresh(vaccine_db)
        return VaccineID.model_validate(vaccine_db)

    @classmethod
    async def delete_vaccine(cls, vaccine_id: int, session: AsyncSession) -> bool:
        query = delete(VaccineBase).where(VaccineBase.id == vaccine_id)
        result = await session.execute(query)
        await session.commit()
        # result.rowcount показывает, сколько строк было затронуто (0 или 1)
        return result.rowcount > 0
