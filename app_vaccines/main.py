from contextlib import asynccontextmanager
from models.db_models import create_tables, delete_tables
from fastapi import FastAPI

from routers import vaccines

@asynccontextmanager
async def lifespan_async(application: FastAPI):
    await create_tables()
    yield
    await delete_tables()

app = FastAPI(
    title="API для отслеживания своих вакцинаций",
    description="API создано для внесения информации о своих вакцинациях. "
                "Нет связей с медицинской организацией. Введеные данные не проверяются в системах ОМС или ДМС.",
    version="0.0.1",
    lifespan=lifespan_async
)

app.include_router(vaccines.router)

@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в API"}
