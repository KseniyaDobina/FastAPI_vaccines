from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app_vaccines.auth.dependencies import get_current_user
from app_vaccines.models.database import get_session
from app_vaccines.models.db_models import User
from app_vaccines.models.repository import UserRepository
from app_vaccines.models.schemas import CurrentUser


async def pagination_parameters(
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=20),
):
    return {"skip": skip, "limit": limit}


async def get_current_db_user(
        current_user: CurrentUser = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)
) -> User:
    """
    Возвращает локального пользователя по данным из JWT.
    """
    user = await UserRepository.get_user_id(current_user, session)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Пользователь не создан в сервисе, нужно его создать в users")
    return user


async def get_current_user_id(
        user: User = Depends(get_current_db_user),
) -> int:
    """
    Возвращает id локального пользователя по данным из JWT.
    """
    return user.id
