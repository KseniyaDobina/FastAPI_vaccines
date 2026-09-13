from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app_vaccines.auth.dependencies import get_current_user
from app_vaccines.models.database import get_session
from app_vaccines.models.db_models import User
from app_vaccines.models.repository import UserRepository, UserResponse
from app_vaccines.models.schemas import CurrentUser
from app_vaccines.routers import depends

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"]
)


@router.get("/me", response_model=UserResponse)
async def get_user(
        session: AsyncSession = Depends(get_session), # noqa: B008
        user: User = Depends(depends.get_current_db_user) # noqa: B008
):
    return user


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
        session: AsyncSession = Depends(get_session), # noqa: B008
        current_user: CurrentUser = Depends(get_current_user) # noqa: B008
):
    """Создание нового пользователя в сервисе
    """
    user = await UserRepository.create_user(current_user, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пользователь уже создан")
    return {"message": "Создался новый пользователь", "user": user}
