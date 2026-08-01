from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from models.schemas import Vaccine
from routers import depends

router = APIRouter(
    prefix="/vaccines",
    tags=["Вакцины"],
)

fake_database = []

@router.get("")
def vaccines(pagination: dict = Depends(depends.pagination_parameters)):
    skip = pagination["skip"]
    limit = pagination["limit"]
    return {"message": "Список вакцин",
            "skip": skip,
            "limit": limit,
            "vaccines": fake_database}

@router.get("/{vaccine_id}")
def get_vaccines(vaccine_id: int):
    for idx, vaccine in enumerate(fake_database):
        if vaccine["id"] == vaccine_id:
            return {"message": f"Информация о вакцине №{vaccine_id}",
                    "vaccine": vaccine}

    raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")

@router.post("")
def create_vaccines(vaccine: Vaccine):
    """
    Создание записи о новой вакцинации
    :param vaccine: вакцина
    :return: 201 если создана, в других случаях ошибку
    """
    new_vaccine = vaccine.model_dump()
    new_vaccine["id"] = len(fake_database) + 1
    fake_database.append(new_vaccine)
    return {"message": f"Добавлена вакцина {new_vaccine['id']}",
            "vaccine": vaccine}

@router.put("/{vaccine_id}")
def put_vaccines(vaccine_id: int, vaccine: Vaccine):
    """
    Обновление информации о вакцинации
    :param vaccine_id: id вакцины
    :return:
    """
    for idx, vaccine_count in enumerate(fake_database):
        if vaccine_count["id"] == vaccine_id:
            updated_vaccine = vaccine.model_dump()
            updated_vaccine["id"] = vaccine_id
            fake_database[idx] = updated_vaccine
            return {"message": f"Полностью зменены данные о вакцине №{vaccine_id}",
                    "vaccine": updated_vaccine}

    raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")

@router.patch("/{vaccine_id}")
def patch_vaccines(vaccine_id: int):
    return {"message": f"Частично изменены данные о вакцине №{vaccine_id}"}

@router.delete("/{vaccine_id}")
def delete_vaccines(vaccine_id: int):
    for idx, vaccine in enumerate(fake_database):
        if vaccine["id"] == vaccine_id:
            del fake_database[idx]
            return {"message": f"Удалена вакцина №{vaccine_id}"}

    raise HTTPException(status_code=404, detail="Данные о вакцинации не найдены")
