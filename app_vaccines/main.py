from contextlib import asynccontextmanager
from fastapi import FastAPI

from app_vaccines.models.database import create_database, delete_database
from app_vaccines.routers import vaccines

@asynccontextmanager
async def lifespan_async(application: FastAPI):
    await create_database()
    yield
    # await delete_database() Пока ничего удалять не будем

app = FastAPI(
    title="API для отслеживания своих вакцинаций",
    description="API создано для внесения информации о своих вакцинациях. "
                "Нет связей с медицинской организацией. Введеные данные не проверяются в системах ОМС или ДМС.",
    version="0.0.1",
    lifespan=lifespan_async
)

app.include_router(vaccines.router)

# @app.get("/")
# async def read_root():
#     return {"message": "Добро пожаловать в API"}
