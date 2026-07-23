import requests
from config import settings

# Проверка авторизации, должна быть ошибка 401
response = requests.get(
            f"{settings.BASE_URL}/api/users")
print(response)

# Проверка, что аторизованный пользователь может сделать запрос и получит 200
headers = {
    "x-api-key": settings.USER_KEY,
}
response = requests.get(
            f"{settings.BASE_URL}/api/users", headers=headers)
print(response)

