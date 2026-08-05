from fastapi import APIRouter, HTTPException, Depends

from models.repository import VaccineRepository, VaccineService
from models.schemas import VaccineCreate, VaccineID
from routers import depends

router = APIRouter(
    prefix="/vaccines",
    tags=["Вакцины"],
)

fake_database = []

@router.get("")
async def get_all_vaccines(pagination: dict = Depends(depends.pagination_parameters)):
    """
    Получение списка всех вакцин
    :param pagination: пагинация ограничивает количество вакцин
    :return: список вакцин
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
    :param vaccine: вакцина
    :return: 201 если создана, в других случаях ошибку
    """
    new_vaccine = await VaccineRepository.add_vaccines(vaccine)
    return {"message": f"Добавлена вакцина {new_vaccine.id}",
            "vaccine": new_vaccine}

@router.get("/{vaccine_id}")
async def get_vaccine(vaccine_id: int):
    """
    Поиск вакцины по id
    :param vaccine_id: id вакцины в базе данных
    :return: информацию о вакцине или ошибку 404
    """
    vaccine = await VaccineRepository.get_vaccine_by_id(vaccine_id)
    if vaccine:
        return {"message": f"Информация о вакцине №{vaccine.id}",
                "vaccine": vaccine}
    raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")

@router.put("/{vaccine_id}")
async def put_vaccine(vaccine_id: int, vaccine: VaccineCreate):
    """
    Обновление информации о вакцинации
    :param vaccine_id: id вакцины
    :return:
    """
    vaccine_db = await VaccineService.update_vaccine(vaccine_id, vaccine)
    if vaccine_db:
        return {"message": f"Информация о вакцине №{vaccine_db.id} изменена",
                "vaccine": vaccine}
    raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")
    # for idx, vaccine_count in enumerate(fake_database):
    #     if vaccine_count["id"] == vaccine_id:
    #         updated_vaccine = vaccine.model_dump()
    #         updated_vaccine["id"] = vaccine_id
    #         fake_database[idx] = updated_vaccine
    #         return {"message": f"Полностью заменены данные о вакцине №{vaccine_id}",
    #                 "vaccine": updated_vaccine}
    #
    # raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")

@router.patch("/{vaccine_id}")
async def patch_vaccine(vaccine_id: int):
    return {"message": f"Частично изменены данные о вакцине №{vaccine_id}"}

@router.delete("/{vaccine_id}")
async def delete_vaccine(vaccine_id: int):
    for idx, vaccine in enumerate(fake_database):
        if vaccine["id"] == vaccine_id:
            del fake_database[idx]
            return {"message": f"Удалена вакцина №{vaccine_id}"}

    raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")
