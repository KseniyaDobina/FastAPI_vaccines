# 💉 Vaccines API

> REST API для ведения личного журнала вакцинации.

Во многих медицинских учреждениях информация о ранее сделанных прививках хранится в разных системах или вовсе теряется
при смене поликлиники. Цель проекта — простой REST API для хранения собственной истории вакцинации, с
JWT-аутентификацией через Keycloak, Repository pattern, асинхронной работой с БД и автоматизированными тестами.

> ⚠️ Важно: API не связано с государственными или частными медицинскими учреждениями. Все данные вводятся пользователем
> вручную и не проверяются через системы ОМС, ДМС или другие медицинские сервисы.

---

## 🚀 Quick Start

```bash
git clone https://github.com/KseniyaDobina/FastAPI_vaccines.git
cd FastAPI_vaccines
cp .env.example .env   # заполнить PATH_TO_DB, KEYCLOAK_URL, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID
docker-compose up
```

После запуска документация доступна на [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

Без Docker:

```bash
pip install -r requirements.txt
uvicorn app_vaccines.main:app --reload
```

### Запуск тестов

(реальный Keycloak не требуется — авторизация в тестах подменяется, а JWT-проверка тестируется на самостоятельно
сгенерированной тестовой RSA-паре):

```bash
pytest
```

---

## 🛠 Стек технологий

| Technology              | Purpose                                  |
|-------------------------|------------------------------------------|
| Python 3.13             | Основной язык                            |
| FastAPI                 | REST API framework                       |
| Pydantic                | Валидация и схемы данных                 |
| pydantic-settings       | Валидация конфигурации из env-переменных |
| SQLAlchemy 2.x          | ORM (async)                              |
| SQLite / aiosqlite      | База данных                              |
| Uvicorn                 | ASGI server                              |
| PyJWT                   | Проверка JWT (RS256, JWKS)               |
| HTTPX                   | Асинхронный HTTP-клиент                  |
| Keycloak                | Аутентификация (OIDC)                    |
| Pytest / pytest-asyncio | Тестирование                             |
| Docker                  | Контейнеризация                          |
| GitHub Actions          | CI                                       |

---

## ✨ Возможности

**Vaccinations** — полный CRUD для записей о вакцинации: список с пагинацией (максимум 20 записей за раз), получение по
ID, создание, полное (`PUT`) и частичное (`PATCH`) обновление, удаление. Валидация входных данных и связанных дат
согласована между слоями — `PATCH` только с одним из связанных полей отдаёт `422`, как и создание с обоими полями сразу.

**Authentication** — JWT-аутентификация с интеграцией Keycloak: подпись токена (RS256), `audience` и `issuer`
проверяются на каждый запрос; OIDC-конфигурация и публичные ключи получаются асинхронно и кэшируются в памяти процесса,
с самовосстановлением кэша при ротации ключей на стороне Keycloak.

**Изоляция данных** — каждый пользователь видит и может изменять только свои записи, на уровне SQL-запросов, а не
постфактум в Python.

Подробности — структура данных и список эндпоинтов ниже, в разделе 'API Reference'.

---

## Архитектура приложения

```text
Client
  │
  │ HTTP + JWT
  ▼
┌─────────────────────┐
│       FastAPI       │
├─────────────────────┤
│      Routers        │
├─────────────────────┤
│ Authentication      │
├─────────────────────┤
│     Repository      │
├─────────────────────┤
│    SQLAlchemy       │
└──────────┬──────────┘
           │
           ▼
        SQLite
```

Разделение ответственности: `routers/` — HTTP-слой, `auth/` — проверка JWT и получение текущего пользователя,
`models/repository.py` — доступ к БД и бизнес-логика, `models/db_models.py` / `schemas.py` — ORM-модели и
Pydantic-схемы.

---

## 🧪 Тестирование

```bash
pytest
```

Тесты разделены по доменам:

```text
tests/
├── conftest.py
├── config.py
├── auth/
│   └── test_keycloak.py       # проверка JWT без реального Keycloak
├── users/
│   └── test_users.py
└── vaccines/
    ├── test_unauthenticated.py
    ├── test_create.py
    ├── test_read.py
    ├── test_update.py
    ├── test_delete.py
    └── test_isolation.py
```

Покрыто: CRUD по вакцинациям и границы пагинации, валидация входных данных и связанных дат, обработка отсутствующих
записей, изоляция данных между пользователями, работа с пользователями, а также проверка JWT — валидный токен, истёкший
срок действия, неверные `audience`/`issuer`, поддельная подпись, неизвестный `kid`, самовосстановление кэша ключей при
ротации.

Для тестов используется отдельная SQLite database и dependency overrides FastAPI; для тестов авторизации —
самостоятельно сгенерированная тестовая RSA-пара вместо реального Keycloak.

---

## 📌 Планируемые улучшения

* поиск по заболеванию, фильтрация и сортировка;
* PostgreSQL + Alembic migrations;
* вынос повторяющейся проверки пользователя (`get_current_user_id`) в общую зависимость по всем роутерам;
* индекс/уникальность на `User.keycloak_id`;
* явный `response_model` для `/users/me` вместо сырого payload из токена;
* линтер и mypy в CI, coverage-отчёт;
* production-ready configuration (CORS, rate limiting);
* улучшение Docker setup и OpenAPI examples.

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
│   └── main.py
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
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
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

API использует Bearer JWT authentication. Приложение получает OIDC-конфигурацию и JWKS от Keycloak асинхронно
(`httpx.AsyncClient`, без блокировки event loop) и использует их для проверки подписи, `audience` и `issuer` каждого
JWT. Результат кэшируется в памяти процесса; при ротации ключей на стороне Keycloak кэш обновляется автоматически.

Настройки приложения (`PATH_TO_DB`, `KEYCLOAK_URL`, `KEYCLOAK_REALM`, `KEYCLOAK_CLIENT_ID`) описаны через
`pydantic-settings` и валидируются при старте: если переменная не задана, приложение упадёт сразу при импорте с понятной
ошибкой. Локально переменные читаются из `.env` (см. `.env.example`), в CI — задаются в `.github/workflows/tests.yml`.

</details>

---

## 👩‍💻 Author

**Kseniya Dobina**

## 📄 License

Проект создан в учебных целях.
