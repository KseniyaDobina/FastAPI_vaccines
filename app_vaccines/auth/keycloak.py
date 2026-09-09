from fastapi import HTTPException, status
from functools import lru_cache
import httpx
import jwt

from app_vaccines.config.settings import Settings

ISSUER = f"{Settings.KEYCLOAK_URL}/realms/{Settings.KEYCLOAK_REALM}"

OIDC_CONFIG_URL = (
    f"{ISSUER}/.well-known/openid-configuration"
)


@lru_cache
def get_oidc_config() -> dict:
    response = httpx.get(OIDC_CONFIG_URL)
    response.raise_for_status()

    return response.json()


@lru_cache
def get_jwks_client() -> jwt.PyJWKClient:
    config = get_oidc_config()

    return jwt.PyJWKClient(
        config["jwks_uri"]
    )


def decode_token(token: str) -> dict:
    try:
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=Settings.KEYCLOAK_CLIENT_ID,
            issuer=ISSUER,
        )

        return payload

    except jwt.PyJWTError as exc:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from exc
