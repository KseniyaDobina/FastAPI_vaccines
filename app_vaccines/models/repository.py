from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app_vaccines.models.db_models import Vaccine, User
from app_vaccines.models.schemas import VaccineCreate, VaccineID, VaccineUpdate, CurrentUser, UserResponse

class VaccineRepository:
    """
    Класс для получения информации о вакцинах.
    Добавления, изменения или удаления вакцин
    """
    @classmethod
    async def get_vaccines(cls, session: AsyncSession) -> list[VaccineID]:
        query = select(Vaccine)
        result = await session.execute(query)
        vaccine_models = result.scalars().all()
        vaccines = [VaccineID.model_validate(vaccine_model) for vaccine_model in vaccine_models]
        return vaccines

    @classmethod
    async def get_vaccine_by_id(cls, vaccine_id: int, session: AsyncSession):
        query = select(Vaccine).where(Vaccine.id == vaccine_id)
        result = await session.execute(query)
        vaccine = result.scalar_one_or_none()
        if vaccine is None:
            return None
        return VaccineID.model_validate(vaccine)

    @classmethod
    async def add_vaccine(cls, vaccine: VaccineCreate, user_id:int, session: AsyncSession) -> VaccineID:
        data = vaccine.model_dump()
        # Пока заглушка с добавлением пользователя
        new_vaccine = Vaccine(**data, user_id=user_id)
        session.add(new_vaccine)
        await session.flush()
        await session.commit()
        await session.refresh(new_vaccine)
        return VaccineID.model_validate(new_vaccine)

    @classmethod
    async def update_vaccine(
            cls,
            vaccine_id: int,
            vaccine: VaccineCreate | VaccineUpdate,
            session: AsyncSession
    ) -> VaccineID | None:
        result = await session.execute(select(Vaccine).where(Vaccine.id == vaccine_id))
        vaccine_db = result.scalar_one_or_none()

        if vaccine_db is None:
            return None
        update_data = vaccine.model_dump(exclude_unset=True)
        new_vaccination_date = update_data.get("vaccination_date", vaccine_db.vaccination_date)
        new_expiration_date = update_data.get("expiration_date", vaccine_db.expiration_date)

        if (
                new_expiration_date is not None
                and new_expiration_date <= new_vaccination_date
        ):
            raise ValueError("expiration_date должна быть позже, чем vaccination_date")

        for field, value in update_data.items():
            setattr(vaccine_db, field, value)

        await session.commit()
        await session.refresh(vaccine_db)

        return VaccineID.model_validate(vaccine_db)

    @classmethod
    async def delete_vaccine(cls, vaccine_id: int, session: AsyncSession) -> bool:
        query = delete(Vaccine).where(Vaccine.id == vaccine_id)
        result = await session.execute(query)
        await session.commit()
        # result.rowcount показывает, сколько строк было затронуто (0 или 1)
        return result.rowcount > 0


class UserRepository:

    @classmethod
    async def get_or_create_user(cls, current_user: CurrentUser, session: AsyncSession) -> UserResponse:
        result = await session.execute(select(User).where(User.keycloak_id == current_user.sub))
        user = result.scalar_one_or_none()

        if user:
            return UserResponse.model_validate(user)

        user = User(
            keycloak_id=current_user.sub,
            username=current_user.username,
            email=current_user.email,
        )
        session.add(user)

        await session.commit()
        await session.refresh(user)

        return UserResponse.model_validate(user)
