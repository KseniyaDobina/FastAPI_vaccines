from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from app_vaccines.auth.keycloak import decode_token
from app_vaccines.models.schemas import CurrentUser


KEYCLOAK_URL = "http://localhost:8080"
REALM = "vaccines"
CLIENT_ID = "fastapi"

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=(
        f"{KEYCLOAK_URL}/realms/{REALM}"
        "/protocol/openid-connect/auth"
    ),
    tokenUrl=(
        f"{KEYCLOAK_URL}/realms/{REALM}"
        "/protocol/openid-connect/token"
    ),
    scopes={},
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> CurrentUser:

    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    return CurrentUser.model_validate(payload)
