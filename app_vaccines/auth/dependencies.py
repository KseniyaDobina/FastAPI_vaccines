from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from pydantic import ValidationError

from app_vaccines.auth.keycloak import decode_token
from app_vaccines.config.settings import settings
from app_vaccines.models.schemas import CurrentUser

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=(
        f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/auth"
    ),
    tokenUrl=(
        f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token"
    ),
    scopes={},
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> CurrentUser:
    payload = await decode_token(token)

    try:
        return CurrentUser.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from exc
