# app_vaccines/auth/keycloak.py

import asyncio

import httpx
import jwt
from jwt.algorithms import RSAAlgorithm
from fastapi import HTTPException, status

from app_vaccines.config.settings import settings

ISSUER = f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}"
OIDC_CONFIG_URL = f"{ISSUER}/.well-known/openid-configuration"

_oidc_config: dict | None = None
_jwks_keys: dict[str, RSAAlgorithm] = {}  # kid -> публичный ключ
_lock = asyncio.Lock()


async def get_oidc_config() -> dict:
    global _oidc_config

    if _oidc_config is None:
        async with httpx.AsyncClient() as client:
            response = await client.get(OIDC_CONFIG_URL)
            response.raise_for_status()
            _oidc_config = response.json()

    return _oidc_config


async def _fetch_jwks() -> dict[str, RSAAlgorithm]:
    """Ходит в сеть за JWKS и разбирает ключи. Сеть - только здесь."""
    config = await get_oidc_config()

    async with httpx.AsyncClient() as client:
        response = await client.get(config["jwks_uri"])
        response.raise_for_status()
        jwks = response.json()

    # from_jwk - чистый разбор JSON в объект ключа, без сети
    return {
        key["kid"]: RSAAlgorithm.from_jwk(key)
        for key in jwks["keys"]
    }


async def _get_signing_key(kid: str) -> RSAAlgorithm:
    global _jwks_keys

    if kid not in _jwks_keys:
        async with _lock:
            if kid not in _jwks_keys:  # double-checked locking
                _jwks_keys = await _fetch_jwks()

    key = _jwks_keys.get(kid)

    if key is None:
        # Ключ мог обновиться на стороне Keycloak (ротация) - пробуем один раз освежить кэш
        async with _lock:
            _jwks_keys = await _fetch_jwks()
        key = _jwks_keys.get(kid)

    if key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    return key


async def decode_token(token: str) -> dict:
    try:
        unverified_header = jwt.get_unverified_header(token)  # чистый парсинг, без сети
        kid = unverified_header["kid"]

        signing_key = await _get_signing_key(kid)

        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=settings.KEYCLOAK_CLIENT_ID,
            issuer=ISSUER,
        )

        return payload

    except (jwt.PyJWTError, KeyError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from exc
