from fastapi import APIRouter, Depends

from app_vaccines.auth.dependencies import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


@router.get("/user")
async def get_user(
    current_user: dict = Depends(get_current_user),
):
    return current_user
