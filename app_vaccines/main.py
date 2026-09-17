from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app_vaccines.routers import users, vaccines


@asynccontextmanager
async def lifespan_async(application: FastAPI)  -> AsyncGenerator[None]:
    yield


app = FastAPI(
    title="API для отслеживания своих вакцинаций",
    description="API создано для внесения информации о своих вакцинациях. "
    "Нет связей с медицинской организацией. Введеные данные не проверяются в системах ОМС или ДМС."
    " После аутентификации, чтобы получить доступ к сервису, нужно создать пользователя в сервисе user.",
    version="0.0.1",
    lifespan=lifespan_async,
    swagger_ui_init_oauth={
        "clientId": "fastapi",
        "usePkceWithAuthorizationCodeGrant": True,
    },
)

app.include_router(vaccines.router)
app.include_router(users.router)
