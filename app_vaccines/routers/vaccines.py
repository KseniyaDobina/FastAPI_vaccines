from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app_vaccines.auth.dependencies import get_current_user
from app_vaccines.models.database import get_session
from app_vaccines.models.repository import VaccineRepository, VaccineService, UserRepository
from app_vaccines.models.schemas import (
    VaccineCreate, VaccineUpdate, VaccineAPIResponse, ListVaccineUpdateAPIResponse, MessageAPIResponse, CurrentUser
)
from app_vaccines.routers import depends
router = APIRouter(
    prefix="/vaccines",
    tags=["Вакцины"]
)

@router.get("", response_model=ListVaccineUpdateAPIResponse)
async def get_all_vaccines(
        session: AsyncSession = Depends(get_session),
        pagination: dict = Depends(depends.pagination_parameters),
        current_user: CurrentUser = Depends(get_current_user)):
    """
    Получение списка всех вакцин
    """
    # skip = await pagination["skip"]
    # limit = await pagination["limit"]
    vaccines = await VaccineRepository.get_vaccines(session)
    return {"message": "Список вакцин",
            # "skip": skip,
            # "limit": limit,
            "vaccines": vaccines}

@router.post("", status_code=status.HTTP_201_CREATED, response_model=VaccineAPIResponse)
async def create_vaccine(
        vaccine: VaccineCreate,
        current_user: CurrentUser = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)):
    """
    Создание записи о новой вакцинации
    """
    # Временно напрямую передаем user_id
    new_vaccine = await VaccineService.add_vaccine(vaccine, 1, session)
    return {"message": f"Добавлена вакцина {new_vaccine.id}",
            "vaccine": new_vaccine}

@router.get("/{vaccine_id}", response_model=VaccineAPIResponse)
async def get_vaccine(
        vaccine_id: int,
        current_user: CurrentUser = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)):
    """
    Поиск вакцинации по id
    """
    vaccine = await VaccineRepository.get_vaccine_by_id(vaccine_id, session)
    if vaccine is not None:
        return {"message": f"Информация о вакцине №{vaccine.id}",
                "vaccine": vaccine}

    raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")

@router.put("/{vaccine_id}", response_model=VaccineAPIResponse)
async def put_vaccine(
        vaccine_id: int,
        vaccine: VaccineCreate,
        current_user: CurrentUser = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)):
    """
    Обновление информации о вакцинации
    """
    new_vaccine_db = await VaccineService.update_vaccine(vaccine_id, vaccine, session)
    if new_vaccine_db is not None:
        return {"message": f"Информация о вакцине изменена",
                "vaccine": new_vaccine_db}

    raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")

@router.patch("/{vaccine_id}", response_model=VaccineAPIResponse)
async def patch_vaccine(
        vaccine_id: int,
        vaccine: VaccineUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)):
    """
    Обновление определенной информации о вакцине, можно указать только конкретное поле
    """
    updated_vaccine = await VaccineService.update_vaccine_patch(vaccine_id, vaccine, session)
    if updated_vaccine is None:
        raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")

    return {"message": f"Информация о вакцине №{updated_vaccine.id} изменена",
            "vaccine": updated_vaccine}

@router.delete("/{vaccine_id}", response_model=MessageAPIResponse)
async def delete_vaccine(
        vaccine_id: int,
        current_user: CurrentUser = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)):
    """
    Удаление записи о вакцинации
    """
    result = await VaccineService.delete_vaccine(vaccine_id, session)
    if result:
        return {"message": f"Удалена вакцина №{vaccine_id}"}

    raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")
