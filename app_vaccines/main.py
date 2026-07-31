from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"Общая страница"}

@app.get("/vaccines")
def vaccines(skip: int = 0, limit: int = 20):
    return {"message": "Список вакцин",
            "skip": skip,
            "limit": limit}

@app.get("/vaccines/{vaccine_id}")
def get_vaccines(vaccine_id: int):
    return {"message": f"Вакцина №{vaccine_id}"}

@app.post("/vaccines")
def post_vaccines(vaccine_id: int):
    number = 0
    return {"message": f"Добавлена вакцина №{number}"}

@app.put("/vaccines/{vaccine_id}")
def put_vaccines(vaccine_id: int):
    return {"message": f"Полностью зменены данные о вакцине №{vaccine_id}"}

@app.patch("/vaccines/{vaccine_id}")
def patch_vaccines(vaccine_id: int):
    return {"message": f"Частично изменены данные о вакцине №{vaccine_id}"}

@app.delete("/vaccines/{vaccine_id}")
def delete_vaccines(vaccine_id: int):
    return {"message": f"Удалена вакцина №{vaccine_id}"}