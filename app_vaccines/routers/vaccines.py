from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app_vaccines.auth.dependencies import get_current_user
from app_vaccines.models.database import get_session
from app_vaccines.models.repository import VaccineRepository, UserRepository
from app_vaccines.models.schemas import VaccineCreate, VaccineUpdate, VaccineID, MessageAPIResponse, CurrentUser
from app_vaccines.routers import depends

router = APIRouter(
    prefix="/vaccines",
    tags=["Вакцины"]
)

@router.get("", response_model=list[VaccineID])
async def get_all_vaccines(
        session: AsyncSession = Depends(get_session),
        pagination: dict = Depends(depends.pagination_parameters),
        current_user: CurrentUser = Depends(get_current_user)):
    """
    Получение списка всех вакцин
    """
    user_id = await UserRepository.get_user(current_user, session)

    if user_id is None:
        raise HTTPException(status_code=401, detail="Пользователь не создан в сервисе, нужно его создать в users")
    # skip = await pagination["skip"]
    # limit = await pagination["limit"]
    vaccines = await VaccineRepository.get_vaccines(user_id, session)

    return vaccines

@router.post("", status_code=status.HTTP_201_CREATED, response_model=VaccineID)
async def create_vaccine(
        vaccine: VaccineCreate,
        current_user: CurrentUser = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)):
    """
    Создание записи о новой вакцинации
    """
    user_id = await UserRepository.get_user(current_user, session)

    if user_id is None:
        raise HTTPException(status_code=401, detail="Пользователь не создан в сервисе, нужно его создать в users")

    new_vaccine = await VaccineRepository.add_vaccine(vaccine, user_id, session)

    return new_vaccine

@router.get("/{vaccine_id}", response_model=VaccineID)
async def get_vaccine(
        vaccine_id: int,
        current_user: CurrentUser = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)):
    """
    Поиск вакцинации по id
    """
    user_id = await UserRepository.get_user(current_user, session)

    if user_id is None:
        raise HTTPException(status_code=401, detail="Пользователь не создан в сервисе, нужно его создать в users")

    vaccine = await VaccineRepository.get_vaccine_by_id(vaccine_id, user_id, session)

    if vaccine is None:
        raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")

    return vaccine

@router.put("/{vaccine_id}", response_model=VaccineID)
async def put_vaccine(
        vaccine_id: int,
        vaccine: VaccineCreate,
        current_user: CurrentUser = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)):
    """
    Обновление информации о вакцинации
    """
    user_id = await UserRepository.get_user(current_user, session)

    if user_id is None:
        raise HTTPException(status_code=401, detail="Пользователь не создан в сервисе, нужно его создать в users")

    new_vaccine_db = await VaccineRepository.update_vaccine(vaccine_id, vaccine, user_id, session)

    if new_vaccine_db is None:
        raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")

    return new_vaccine_db

@router.patch("/{vaccine_id}", response_model=VaccineID)
async def patch_vaccine(
        vaccine_id: int,
        vaccine: VaccineUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)):
    """
    Обновление определенной информации о вакцине, можно указать только конкретное поле
    """
    user_id = await UserRepository.get_user(current_user, session)

    if user_id is None:
        raise HTTPException(status_code=401, detail="Пользователь не создан в сервисе, нужно его создать в users")

    updated_vaccine = await VaccineRepository.update_vaccine(vaccine_id, vaccine, user_id, session)

    if updated_vaccine is None:
        raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")

    return updated_vaccine

@router.delete("/{vaccine_id}", response_model=MessageAPIResponse)
async def delete_vaccine(
        vaccine_id: int,
        current_user: CurrentUser = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)):
    """
    Удаление записи о вакцинации
    """
    user_id = await UserRepository.get_user(current_user, session)

    if user_id is None:
        raise HTTPException(status_code=401, detail="Пользователь не создан в сервисе, нужно его создать в users")

    result = await VaccineRepository.delete_vaccine(vaccine_id, user_id, session)

    if result:
        return {"message": f"Удалена вакцина №{vaccine_id}"}

    raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")
