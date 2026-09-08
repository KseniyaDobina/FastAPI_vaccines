from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer

from app_vaccines.auth.keycloak import decode_token
from app_vaccines.config.settings import Settings
from app_vaccines.models.schemas import CurrentUser

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=(
        f"{Settings.KEYCLOAK_URL}/realms/{Settings.KEYCLOAK_REALM}"
        "/protocol/openid-connect/auth"
    ),
    tokenUrl=(
        f"{Settings.KEYCLOAK_URL}/realms/{Settings.KEYCLOAK_REALM}"
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
