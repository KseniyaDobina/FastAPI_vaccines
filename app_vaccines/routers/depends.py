from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app_vaccines.auth.dependencies import get_current_user
from app_vaccines.models.database import get_session
from app_vaccines.models.repository import UserRepository
from app_vaccines.models.schemas import CurrentUser


async def pagination_parameters(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}


async def get_current_user_id(
        current_user: CurrentUser = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
) -> int:
    """
    Возвращает id локального пользователя по данным из JWT.
    Бросает 401, если пользователь ещё не зарегистрирован в сервисе (users/me).
    """
    user_id = await UserRepository.get_user(current_user, session)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не создан в сервисе, нужно его создать в users",
        )

    return user_id
