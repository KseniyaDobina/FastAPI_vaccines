from fastapi import APIRouter, HTTPException, Depends

from app_vaccines.models.repository import VaccineRepository, VaccineService
from app_vaccines.models.schemas import VaccineCreate, VaccineID
from app_vaccines.routers import depends

router = APIRouter(
    prefix="/vaccines",
    tags=["Вакцины"],
    # response_model=VaccineID
)

@router.get("")
async def get_all_vaccines(pagination: dict = Depends(depends.pagination_parameters)):
    """
    Получение списка всех вакцин
    """
    skip = pagination["skip"]
    limit = pagination["limit"]
    vaccines = await VaccineRepository.get_vaccines()
    return {"message": "Список вакцин",
            "skip": skip,
            "limit": limit,
            "vaccines": vaccines}

@router.post("")
async def create_vaccine(vaccine: VaccineCreate = Depends()):
    """
    Создание записи о новой вакцинации
    """
    new_vaccine = await VaccineService.add_vaccine(vaccine)
    return {"message": f"Добавлена вакцина {new_vaccine.id}",
            "vaccine": new_vaccine}

@router.get("/{vaccine_id}")
async def get_vaccine(vaccine_id: int):
    """
    Поиск вакцинации по id
    """
    vaccine = await VaccineRepository.get_vaccine_by_id(vaccine_id)
    if vaccine is not None:
        return {"message": f"Информация о вакцине №{vaccine.id}",
                "vaccine": vaccine}
    raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")

@router.put("/{vaccine_id}")
async def put_vaccine(vaccine_id: int, vaccine: VaccineCreate):
    """
    Обновление информации о вакцинации
    """
    new_vaccine_db = await VaccineService.update_vaccine(vaccine_id, vaccine)
    if new_vaccine_db is not None:
        return {"message": f"Информация о вакцине № изменена",
                "vaccine": new_vaccine_db.id}
    raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")

@router.patch("/{vaccine_id}")
async def patch_vaccine(vaccine_id: int, vaccine: VaccineCreate):
    return {"message": f"Частично изменены данные о вакцине №{vaccine_id}"}

@router.delete("/{vaccine_id}")
async def delete_vaccine(vaccine_id: int):
    """Удаление записи о вакцинации"""
    result = await VaccineService.delete_vaccine(vaccine_id)
    if result:
        return {"message": f"Удалена вакцина №{vaccine_id}"}
    raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")
