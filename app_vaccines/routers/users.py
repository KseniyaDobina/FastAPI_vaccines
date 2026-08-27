from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app_vaccines.auth.dependencies import get_current_user
from app_vaccines.models.database import get_session
from app_vaccines.models.repository import VaccineRepository, VaccineService, UserRepository


router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


@router.get("/user")
async def get_user(session: AsyncSession = Depends(get_session), current_user: dict = Depends(get_current_user)):
    user = await (UserRepository.get_or_create_user(current_user, session))
    return user
