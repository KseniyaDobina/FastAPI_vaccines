from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app_vaccines.models.database import get_session
from app_vaccines.models.repository import VaccineRepository, VaccineService
from app_vaccines.models.schemas import VaccineCreate, VaccineUpdate, VaccineID, MessageAPIResponse
from app_vaccines.routers import depends

router = APIRouter(
    prefix="/vaccines",
    tags=["Вакцины"]
)


@router.get("", response_model=list[VaccineID])
async def get_all_vaccines(
        session: AsyncSession = Depends(get_session),
        pagination: dict = Depends(depends.pagination_parameters),
        user_id: int = Depends(depends.get_current_user_id)):
    """
    Получение списка всех вакцин
    """

    skip = pagination["skip"]
    limit = pagination["limit"]
    vaccines = await VaccineService.get_vaccines(user_id, skip, limit, session)

    return vaccines


@router.post("", status_code=status.HTTP_201_CREATED, response_model=VaccineID)
async def create_vaccine(
        vaccine: VaccineCreate,
        user_id: int = Depends(depends.get_current_user_id),
        session: AsyncSession = Depends(get_session)):
    """
    Создание записи о новой вакцинации
    """

    new_vaccine = await VaccineService.add_vaccine(vaccine, user_id, session)

    return new_vaccine


@router.get("/{vaccine_id}", response_model=VaccineID)
async def get_vaccine(
        vaccine_id: int,
        user_id: int = Depends(depends.get_current_user_id),
        session: AsyncSession = Depends(get_session)):
    """
    Поиск вакцинации по id
    """

    vaccine = await VaccineService.get_vaccine_by_id(vaccine_id, user_id, session)

    if vaccine is None:
        raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")

    return vaccine


@router.put("/{vaccine_id}", response_model=VaccineID)
async def put_vaccine(
        vaccine_id: int,
        vaccine: VaccineCreate,
        user_id: int = Depends(depends.get_current_user_id),
        session: AsyncSession = Depends(get_session)):
    """
    Обновление информации о вакцинации
    """

    new_vaccine_db = await VaccineService.update_vaccine(vaccine_id, vaccine, user_id, session)

    if new_vaccine_db is None:
        raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")

    return new_vaccine_db


@router.patch("/{vaccine_id}", response_model=VaccineID)
async def patch_vaccine(
        vaccine_id: int,
        vaccine: VaccineUpdate,
        user_id: int = Depends(depends.get_current_user_id),
        session: AsyncSession = Depends(get_session)):
    """
    Обновление определенной информации о вакцине, можно указать только конкретное поле
    """
    updated_vaccine = await VaccineService.update_vaccine(vaccine_id, vaccine, user_id, session)

    if updated_vaccine is None:
        raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")

    return updated_vaccine


@router.delete("/{vaccine_id}", response_model=MessageAPIResponse)
async def delete_vaccine(
        vaccine_id: int,
        user_id: int = Depends(depends.get_current_user_id),
        session: AsyncSession = Depends(get_session)):
    """
    Удаление записи о вакцинации
    """

    result = await VaccineRepository.delete_vaccine(vaccine_id, user_id, session)

    if result:
        return {"message": f"Удалена вакцина №{vaccine_id}"}

    raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")
