from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app_vaccines.models.database import get_session
from app_vaccines.models.repository import VaccineRepository, VaccineService
from app_vaccines.models.schemas import VaccineCreate, VaccineID
from app_vaccines.routers import depends

router = APIRouter(
    prefix="/vaccines",
    tags=["Вакцины"],
    # response_model=VaccineID
)

@router.get("")
async def get_all_vaccines(session: AsyncSession = Depends(get_session), pagination: dict = Depends(depends.pagination_parameters)):
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

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_vaccine(vaccine: VaccineCreate, session: AsyncSession = Depends(get_session)):
    """
    Создание записи о новой вакцинации
    """
    new_vaccine = await VaccineService.add_vaccine(vaccine, session)
    return {"message": f"Добавлена вакцина {new_vaccine.id}",
            "vaccine": new_vaccine}

@router.get("/{vaccine_id}")
async def get_vaccine(vaccine_id: int, session: AsyncSession = Depends(get_session)):
    """
    Поиск вакцинации по id
    """
    vaccine = await VaccineRepository.get_vaccine_by_id(vaccine_id, session)
    if vaccine is not None:
        return {"message": f"Информация о вакцине №{vaccine.id}",
                "vaccine": vaccine}
    raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")

@router.put("/{vaccine_id}")
async def put_vaccine(vaccine_id: int, vaccine: VaccineCreate, session: AsyncSession = Depends(get_session)):
    """
    Обновление информации о вакцинации
    """
    new_vaccine_db = await VaccineService.update_vaccine(vaccine_id, vaccine, session)
    if new_vaccine_db is not None:
        return {"message": f"Информация о вакцине № изменена",
                "vaccine": new_vaccine_db.id}
    raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")

@router.patch("/{vaccine_id}")
async def patch_vaccine(vaccine_id: int, vaccine: VaccineCreate):
    return {"message": f"Частично изменены данные о вакцине №{vaccine_id}"}

@router.delete("/{vaccine_id}")
async def delete_vaccine(vaccine_id: int, session: AsyncSession = Depends(get_session)):
    """Удаление записи о вакцинации"""
    result = await VaccineService.delete_vaccine(vaccine_id, session)
    if result:
        return {"message": f"Удалена вакцина №{vaccine_id}"}
    raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")
