from fastapi import FastAPI

from routers import vaccines

app = FastAPI(
    title="API для отслеживания своих вакцинаций",
    description="API создано для внесения информации о своих вакцинациях. "
                "Нет связей с медицинской организацией. Введеные данные нигде не проверяются.",
    version="0.0.1",
)

app.include_router(vaccines.router)

@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в API"}
