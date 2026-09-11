import time

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from app_vaccines.auth import keycloak
from app_vaccines.config.settings import settings

from fastapi import HTTPException

TEST_KID = "test-kid-1"


@pytest.fixture
def rsa_private_key():
    """
    'Правильный' ключ - имитация настоящего ключа Keycloak.
    """

    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def other_rsa_private_key():
    """
    Второй, 'чужой' ключ - имитация злоумышленника без доступа к настоящему ключу Keycloak.
    """

    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def jwks_document(rsa_private_key):
    """
    превращает публичную часть тестового ключа в тот самый JSON-формат, который в реальности отдаёт Keycloak
    """

    # обратная операция к тому from_jwk(...)
    public_jwk = jwt.algorithms.RSAAlgorithm.to_jwk(
        rsa_private_key.public_key(), as_dict=True
    )
    public_jwk["kid"] = TEST_KID
    public_jwk["use"] = "sig"
    public_jwk["alg"] = "RS256"
    return {"keys": [public_jwk]}


@pytest.fixture
def oidc_config():
    return {
        "issuer": keycloak.ISSUER,
        "jwks_uri": f"{keycloak.ISSUER}/protocol/openid-connect/certs",
    }


class _FakeResponse:
    """
    "Муляж", который притворяется httpx.Response, но на самом деле просто хранит один заранее заготовленный словарь
    (_json_data) и отдаёт его через .json()
    """

    def __init__(self, json_data):
        self._json_data = json_data

    def raise_for_status(self):
        pass

    def json(self):
        return self._json_data


@pytest.fixture(autouse=True)
def reset_keycloak_cache():
    """
    _oidc_config и _jwks_keys - переменные модуля.
    (autouse=True, то есть применяется ко всем тестам в файле автоматически) — обнуляет модульные кэши
    _oidc_config/_jwks_keys до и после каждого теста. Без этого первый тест реально сходил бы в "сеть" (замоканную),
    закэшировал бы ключ, а все следующие тесты тихо работали бы с этим кэшем — то есть по факту вообще
    не проверял бы код внутри _fetch_jwks
    """

    keycloak._oidc_config = None
    keycloak._jwks_keys = {}
    yield
    keycloak._oidc_config = None
    keycloak._jwks_keys = {}


@pytest.fixture
def mock_keycloak_network(monkeypatch, oidc_config, jwks_document):
    """
    Подменяет httpx.AsyncClient.get так, чтобы код думал, что реально сходил в сеть,
    а на самом деле получил заготовленные ответы.
    Заодно считает, сколько раз реально "сходили" за конфигом/ключами — это нужно для последнего теста на кэширование.
    """

    calls = {"oidc": 0, "jwks": 0}

    async def fake_get(self, url, *args, **kwargs):
        if url == keycloak.OIDC_CONFIG_URL:
            calls["oidc"] += 1
            return _FakeResponse(oidc_config)
        if url == oidc_config["jwks_uri"]:
            calls["jwks"] += 1
            return _FakeResponse(jwks_document)
        raise AssertionError(f"Неожиданный запрос в тесте: {url}")

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)
    return calls


def make_token(private_key, kid=TEST_KID, **overrides):
    """
    Маленькая "фабрика" тестовых токенов с разумными дефолтами (правильный iss/aud, срок годности 5 минут),
    где конкретный тест переопределяет только то, что хочет сломать (exp, aud, iss, kid)
    """

    now = int(time.time())
    payload = {
        "iss": keycloak.ISSUER,
        "aud": settings.KEYCLOAK_CLIENT_ID,
        "sub": "test-user-id",
        "preferred_username": "testuser",
        "iat": now,
        "exp": now + 300,
    }
    payload.update(overrides)

    return jwt.encode(payload, private_key, algorithm="RS256", headers={"kid": kid})


@pytest.mark.asyncio
async def test_decode_token_valid(mock_keycloak_network, rsa_private_key):
    """
    Всё как надо, токен принят, payload с правильными полями
    """

    token = make_token(rsa_private_key)

    payload = await keycloak.decode_token(token)

    assert payload["sub"] == "test-user-id"
    assert payload["preferred_username"] == "testuser"


@pytest.mark.asyncio
async def test_decode_token_expired(mock_keycloak_network, rsa_private_key):
    """
    Просроченный токен отклонён
    """

    token = make_token(rsa_private_key, exp=int(time.time()) - 60)

    with pytest.raises(HTTPException) as exc_info:
        await keycloak.decode_token(token)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_decode_token_wrong_audience(mock_keycloak_network, rsa_private_key):
    """
    Токен не для нашего клиента / не от нашего Keycloak отклонён, даже если подпись математически верна
    """

    token = make_token(rsa_private_key, aud="какой-то-другой-клиент")

    with pytest.raises(HTTPException) as exc_info:
        await keycloak.decode_token(token)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_decode_token_wrong_issuer(mock_keycloak_network, rsa_private_key):
    """
    Токен подписан чужим ключом, но с kid, который совпадает с настоящим.
    Проверяет, что код реально сверяет подпись математически, а не просто смотрит на kid "для галочки"
    """

    token = make_token(rsa_private_key, iss="http://не-наш-keycloak/realms/чужой")

    with pytest.raises(HTTPException) as exc_info:
        await keycloak.decode_token(token)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_decode_token_forged_signature(mock_keycloak_network, other_rsa_private_key):
    """
    Токен подписан ЧУЖИМ приватным ключом, но заявляет тот же kid,
    что и настоящий ключ в JWKS. Проверяем, что математическая
    проверка подписи это ловит, а не просто совпадение kid.
    """

    forged_token = make_token(other_rsa_private_key, kid=TEST_KID)

    with pytest.raises(HTTPException) as exc_info:
        await keycloak.decode_token(forged_token)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_decode_token_unknown_kid(mock_keycloak_network, rsa_private_key):
    """
    Токен ссылается на ключ, которого просто нет в JWKS (ни изначально, ни после попытки обновить кэш) —
    должен упасть в 401, а не в необработанное исключение
    """

    token = make_token(rsa_private_key, kid="кто-то-совсем-другой")

    with pytest.raises(HTTPException) as exc_info:
        await keycloak.decode_token(token)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_oidc_config_is_cached_between_calls(mock_keycloak_network):
    """
    Подтверждает, что кэширование реально работает: второй вызов не идёт повторно в сеть
    """

    await keycloak.get_oidc_config()
    await keycloak.get_oidc_config()

    assert mock_keycloak_network["oidc"] == 1  # а не 2

NEW_KID = "test-kid-2-rotated"


@pytest.fixture
def new_rsa_private_key():
    """Второй ключ - имитация НОВОГО ключа, который Keycloak сгенерировал при ротации."""
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.mark.asyncio
async def test_decode_token_self_heals_on_key_rotation(
        monkeypatch,
        oidc_config,
        rsa_private_key,
        new_rsa_private_key
):
    """
    Сценарий ротации: в кэше (_jwks_keys) уже лежит СТАРЫЙ ключ (как будто
    мы закэшировали JWKS ещё до того, как Keycloak сделал ротацию), а токен
    подписан НОВЫМ ключом, которого в кэше ещё нет. Код должен сам сходить
    в сеть за обновлённым JWKS и найти новый ключ, а не отклонить валидный
    токен как "неизвестный kid".
    """
    old_public_jwk = jwt.algorithms.RSAAlgorithm.to_jwk(
        rsa_private_key.public_key(), as_dict=True
    )
    old_public_jwk["kid"] = TEST_KID

    new_public_jwk = jwt.algorithms.RSAAlgorithm.to_jwk(
        new_rsa_private_key.public_key(), as_dict=True
    )
    new_public_jwk["kid"] = NEW_KID

    # Имитируем "устаревший" кэш: в нём есть только старый ключ
    keycloak._jwks_keys = {
        TEST_KID: jwt.algorithms.RSAAlgorithm.from_jwk(old_public_jwk)
    }
    keycloak._oidc_config = oidc_config  # конфиг тоже уже "закэширован" ранее

    calls = {"jwks": 0}

    async def fake_get(self, url, *args, **kwargs):
        if url == oidc_config["jwks_uri"]:
            calls["jwks"] += 1
            # Keycloak уже отдаёт ОБНОВЛЁННЫЙ набор - старый ключ ещё жив
            # (грейс-период), плюс появился новый
            return _FakeResponse({"keys": [old_public_jwk, new_public_jwk]})
        raise AssertionError(f"Неожиданный запрос в тесте: {url}")

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

    token = make_token(new_rsa_private_key, kid=NEW_KID)

    payload = await keycloak.decode_token(token)

    assert payload["sub"] == "test-user-id"
    assert calls["jwks"] == 1  # кэш обновился за один поход в сеть
    assert NEW_KID in keycloak._jwks_keys  # новый ключ теперь в кэше
    assert TEST_KID in keycloak._jwks_keys  # старый тоже остался (грейс-период)


@pytest.mark.asyncio
async def test_decode_token_retries_once_if_key_still_missing_after_first_refresh(
        monkeypatch, oidc_config, new_rsa_private_key
):
    """
    Более редкий случай: даже ПЕРВЫЙ поход за обновлением ещё не видит
    новый ключ (например, задержка репликации на стороне Keycloak).
    Код должен попробовать обновиться ЕЩЁ РАЗ и только тогда найти ключ.
    """
    new_public_jwk = jwt.algorithms.RSAAlgorithm.to_jwk(
        new_rsa_private_key.public_key(), as_dict=True
    )
    new_public_jwk["kid"] = NEW_KID

    keycloak._jwks_keys = {}  # кэш пуст с самого начала
    keycloak._oidc_config = oidc_config

    calls = {"jwks": 0}

    async def fake_get(self, url, *args, **kwargs):
        if url == oidc_config["jwks_uri"]:
            calls["jwks"] += 1
            if calls["jwks"] == 1:
                return _FakeResponse({"keys": []})  # первый раз - ключа ещё нет нигде
            return _FakeResponse({"keys": [new_public_jwk]})  # второй раз - уже появился
        raise AssertionError(f"Неожиданный запрос в тесте: {url}")

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

    token = make_token(new_rsa_private_key, kid=NEW_KID)

    payload = await keycloak.decode_token(token)

    assert payload["sub"] == "test-user-id"
    assert calls["jwks"] == 2  # понадобилось два похода в сеть
