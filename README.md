# 💉 Vaccines API

> REST API для ведения личного журнала вакцинации.

Во многих медицинских учреждениях информация о ранее сделанных прививках хранится в разных системах или вовсе теряется при смене поликлиники. Цель проекта — простой REST API для хранения собственной истории вакцинации, с JWT-аутентификацией через Keycloak, Repository pattern, асинхронной работой с БД и автоматизированными тестами.

> ⚠️ Важно: API не связано с государственными или частными медицинскими учреждениями. Все данные вводятся пользователем вручную и не проверяются через системы ОМС, ДМС или другие медицинские сервисы.

---

## 🚀 Quick Start

```bash
git clone https://github.com/KseniyaDobina/FastAPI_vaccines.git
cd FastAPI_vaccines
cp .env.example .env                 # для запуска приложения локально (uvicorn на хосте)
cp .env.docker.example .env.docker   # для запуска через docker-compose 
docker-compose up --build
```

Docker-compose поднимает три сервиса: Postgres, Keycloak и само API. Приложение внутри контейнера использует `.env.docker` (хосты вида `postgres`, `keycloak`), а при локальном запуске без Docker `.env` (`localhost`). Разница только в хостах подключения, остальные значения совпадают.
 
После запуска документация доступна на [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs), Keycloak — на
[http://127.0.0.1:8080](http://127.0.0.1:8080).
 
При старте контейнера API миграции Alembic применяются автоматически (`alembic upgrade head`), схему создавать вручную не нужно.
 
Локальный запуск без Docker (Postgres и Keycloak всё равно понадобятся — либо через `docker-compose up postgres keycloak`, либо свои инстансы):

```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn app_vaccines.main:app --reload
```

Для разработки (тесты, линтер, типизация) понадобится ещё один файл зависимостей:
 
```bash
pip install -r requirements.txt -r requirements-dev.txt
```

### Запуск тестов

(реальный Keycloak не требуется — авторизация в тестах подменяется, а JWT-проверка тестируется на самостоятельно сгенерированной тестовой RSA-паре):

```bash
pytest --cov=app_vaccines --cov-report=term-missing
ruff check .
mypy app_vaccines/
```

Все три проверки прогоняются автоматически в CI на каждый push/pull request.

---

## 🛠 Стек технологий

| Technology              | Purpose                                    |
|--------------------------|---------------------------------------------|
| Python 3.14              | Основной язык                              |
| FastAPI                  | REST API framework                         |
| Pydantic                 | Валидация и схемы данных                   |
| pydantic-settings        | Валидация конфигурации из env-переменных   |
| SQLAlchemy 2.x           | ORM (async)                                |
| PostgreSQL / asyncpg     | База данных                                |
| Alembic                  | Миграции схемы БД                          |
| Uvicorn                  | ASGI server                                |
| PyJWT                    | Проверка JWT (RS256, JWKS)                 |
| HTTPX                    | Асинхронный HTTP-клиент                    |
| Keycloak                 | Аутентификация (OIDC)                      |
| Pytest / pytest-asyncio  | Тестирование (на отдельной SQLite БД)      |
| Ruff                     | Линтер (стиль, security, docstrings)       |
| Mypy                     | Статическая проверка типов                 |
| Docker / docker-compose  | Контейнеризация (API, Postgres, Keycloak)  |
| GitHub Actions           | CI (тесты, линтер, типы)                   |
---

## ✨ Возможности

**Vaccinations** — полный CRUD для записей о вакцинации: список с пагинацией (максимум 20 записей за раз), получение по
ID, создание, полное (`PUT`) и частичное (`PATCH`) обновление, удаление. Валидация входных данных и связанных дат
согласована между слоями — `PATCH` только с одним из связанных полей отдаёт `422`, как и создание с обоими полями сразу.
 
**Authentication** — JWT-аутентификация с интеграцией Keycloak: подпись токена (RS256), `audience` и `issuer`
проверяются на каждый запрос; OIDC-конфигурация и публичные ключи получаются асинхронно и кэшируются в памяти процесса,
с самовосстановлением кэша при ротации ключей на стороне Keycloak. Локальный пользователь получается через единую
зависимость (`get_current_db_user`) без повторных запросов к БД, и в ответах API никогда не отдаётся `keycloak_id`.
 
**Изоляция данных** — каждый пользователь видит и может изменять только свои записи, на уровне SQL-запросов, а не
постфактум в Python.

**Схема БД** — управляется через Alembic-миграции (`migrations/`), а не пересоздаётся при каждом старте приложения; поддерживает SQLite (тесты) и PostgreSQL (прод) через общий SQLAlchemy-слой.
 
**Качество кода** — Ruff и Mypy прогоняются в CI на каждый коммит; покрытие тестами измеряется через `pytest-cov`.
 
Подробности — структура данных и список эндпоинтов ниже, в разделе 'API Reference'.

---

## Архитектура приложения

```text
Client
  │
  │ HTTP + JWT
  ▼
┌─────────────────────┐        ┌────────────────┐
│       FastAPI        │◄──────►│    Keycloak     │
├─────────────────────┤  OIDC  │ (аутентификация)│
│      Routers          │        └────────────────┘
├─────────────────────┤
│ Authentication         │
├─────────────────────┤
│     Repository         │
├─────────────────────┤
│    SQLAlchemy           │
└──────────┬──────────┘
           │
           ▼
      PostgreSQL
   (миграции - Alembic)
```

Разделение ответственности: `routers/` — HTTP-слой, `auth/` — проверка JWT и получение текущего пользователя, `models/repository.py` — доступ к БД и бизнес-логика, `models/db_models.py` / `schemas.py` — ORM-модели и Pydantic-схемы, `migrations/` — история изменений схемы БД (Alembic).

---

## 🧪 Тестирование

```bash
pytest --cov=app_vaccines --cov-report=term-missing
```
Текущее покрытие тестами — **98%**.

Тесты разделены по доменам:

```text
tests/
├── conftest.py
├── config.py
├── auth/
│   └── test_keycloak.py       # проверка JWT без реального Keycloak
├── users/
│   ├── test_unauthenticated.py
│   └── test_users.py
└── vaccines/
    ├── test_unauthenticated.py
    ├── test_create.py
    ├── test_read.py
    ├── test_update.py
    ├── test_delete.py
    └── test_isolation.py
```

Покрыто: CRUD по вакцинациям и границы пагинации, валидация входных данных и связанных дат, обработка отсутствующих записей, изоляция данных между пользователями, работа с пользователями, а также проверка JWT — валидный токен, истёкший срок действия, неверные `audience`/`issuer`, поддельная подпись, неизвестный `kid`, самовосстановление кэша ключей при ротации.

Для тестов используется отдельная SQLite database (не Postgres) и dependency overrides FastAPI; для тестов авторизации — самостоятельно сгенерированная тестовая RSA-пара вместо реального Keycloak.

---

## 📌 Планируемые улучшения

* поиск по заболеванию, фильтрация и сортировка;
* пагинация с общим количеством записей (`total`) в ответе;
* CORS и rate limiting;
* структурированное логирование и `/health` эндпоинт;
* прогон тестов на реальном Postgres в CI (сейчас — только SQLite), в дополнение к текущим;
* строгая типизация тестового кода (сейчас `mypy` проверяет только `app_vaccines/`);
* улучшение OpenAPI examples.

---

## 📖 Подробности

###

<details>
<summary>Структура проекта</summary>

```text
FastAPI_vaccines/
│
├── app_vaccines/
│   ├── auth/
│   │   ├── dependencies.py
│   │   └── keycloak.py
│   ├── config/
│   │   └── settings.py
│   ├── models/
│   │   ├── database.py
│   │   ├── db_models.py
│   │   ├── repository.py
│   │   └── schemas.py
│   ├── routers/
│   │   ├── depends.py
│   │   ├── users.py
│   │   └── vaccines.py
│   ├── __init__.py
│   └── main.py
│
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── tests/
│   ├── config.py
│   ├── conftest.py
│   ├── auth/
│   ├── users/
│   └── vaccines/
│
├── .github/workflows/tests.yml
├── .env.example
├── .env.docker.example
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── requirements.txt
└── requirements_dev.txt
```

</details>

<details>
<summary>Модель данных — Vaccine</summary>

| Field              | Type      | Required | Description                             |
|--------------------|-----------|---------:|-----------------------------------------|
| `id`               | `integer` |        — | Уникальный идентификатор                |
| `disease`          | `string`  |       ✅ | Заболевание                             |
| `vaccine_name`     | `string`  |       ✅ | Название вакцины                        |
| `dose_number`      | `string`  |       ✅ | Номер дозы                              |
| `vaccination_date` | `date`    |       ✅ | Дата вакцинации                         |
| `expiration_date`  | `date`    |       ❌ | Дата окончания действия / срок годности |
| `type_vaccine`     | `string`  |       ✅ | Тип вакцины                             |
| `lot`              | `string`  |       ✅ | Номер партии                            |
| `manufacturer`     | `string`  |       ✅ | Производитель                           |
| `clinic`           | `string`  |       ✅ | Медицинская организация                 |
| `country`          | `string`  |       ✅ | Страна                                  |
| `city`             | `string`  |       ✅ | Город                                   |
| `notes`            | `string`  |       ❌ | Дополнительные заметки                  |
| `user_id`          | `integer` |        — | Владелец записи                         |

</details>

<details>
<summary>🔌 API Reference</summary>

### Vaccinations

Все endpoints требуют авторизации.

| Method   | Endpoint                 | Description                                                                   |
|----------|--------------------------|-------------------------------------------------------------------------------|
| `GET`    | `/vaccines`              | Список вакцинаций текущего пользователя (пагинация: `skip`, `limit` до 20)    |
| `GET`    | `/vaccines/{vaccine_id}` | Получить вакцинацию по ID (недоступна, если принадлежит другому пользователю) |
| `POST`   | `/vaccines`              | Создать новую запись вакцинации                                               |
| `PUT`    | `/vaccines/{vaccine_id}` | Полностью обновить вакцинацию                                                 |
| `PATCH`  | `/vaccines/{vaccine_id}` | Изменить только переданные поля                                               |
| `DELETE` | `/vaccines/{vaccine_id}` | Удалить вакцинацию                                                            |

Пример запроса для `POST`:

```json
{
  "disease": "Hepatitis B",
  "vaccine_name": "Engerix-B",
  "dose_number": "1",
  "vaccination_date": "2026-08-20",
  "expiration_date": null,
  "type_vaccine": "Recombinant",
  "lot": "ABC123",
  "manufacturer": "GSK",
  "clinic": "City Clinic",
  "country": "Germany",
  "city": "Frankfurt",
  "notes": "First dose"
}
```

### Users

| Method | Endpoint    | Description                                    |
|--------|-------------|------------------------------------------------|
| `GET`  | `/users/me` | Получить данные текущего пользователя          |
| `POST` | `/users/me` | Создать пользователя (после логина в Keycloak) |

</details>

<details>
<summary>Аутентификация и конфигурация</summary>

API использует Bearer JWT authentication. Приложение получает OIDC-конфигурацию и JWKS от Keycloak асинхронно (`httpx.AsyncClient`, без блокировки event loop) и использует их для проверки подписи, `audience` и `issuer` каждого JWT. Результат кэшируется в памяти процесса; при ротации ключей на стороне Keycloak кэш обновляется автоматически.

Настройки приложения (`PATH_TO_DB`, `KEYCLOAK_URL`, `KEYCLOAK_REALM`, `KEYCLOAK_CLIENT_ID`) описаны через `pydantic-settings` и валидируются при старте: если переменная не задана, приложение упадёт сразу при импорте с понятной ошибкой. 

Два файла окружения — `.env` (локальный запуск) и `.env.docker` (запуск в `docker-compose`); оба исключены из git, примеры — `.env.example` и `.env.docker.example`. В контейнере переменные пробрасываются через `env_file`, а не копируются внутрь образа (`.env` и `.env.docker` явно исключены в `.dockerignore`); в CI — задаются в `.github/workflows/tests.yml`.

</details>

---

## 👩‍💻 Author

**Kseniya Dobina**

## 📄 License

Проект создан в учебных целях.
