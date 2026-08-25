from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app_vaccines.auth.keycloak import decode_token


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:

    return decode_token(credentials.credentials)
