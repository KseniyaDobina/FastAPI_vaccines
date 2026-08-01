import requests
from config import settings


def test_authenticated_user_get_users():
    """
    Проверка, что авторизованный пользователь может сделать запрос и получит 200
    """
    response = get_user(f"{settings.BASE_URL}/api/users")
    print(response.status_code)
    assert response.status_code == 200

def test_unauthenticated_user_get_users():
    """
    Проверка неавторизованного пользователя, должна быть ошибка 401
    """
    response = get_user(f"{settings.BASE_URL}/api/users", False)
    print(response.status_code, response.headers)
    assert response.status_code == 401


# f24c866f81425d2a73cb0015e2e8904d80c6acbb1b979652a80b4db46c91d1e1
