# 💉 Vaccines API

> REST API для ведения личного журнала вакцинации.

Во многих медицинских учреждениях информация о ранее сделанных прививках хранится в разных системах
или вовсе теряется при смене поликлиники. Цель проекта — создать простой REST API
для хранения собственной истории вакцинации.

Проект создан в учебных целях для практики:

* разработки REST API на FastAPI;
* асинхронной работы с базой данных;
* SQLAlchemy 2.x;
* Pydantic;
* JWT-аутентификации и интеграции с Keycloak;
* Repository pattern;
* автоматизированного API-тестирования;
* Docker;
* GitHub Actions CI.

> ⚠️ Важно:
> API не связано с государственными или частными медицинскими учреждениями.
> Все данные вводятся пользователем вручную и не проверяются через системы ОМС, ДМС или другие медицинские сервисы.

---

## ✨ Возможности

### Vaccinations

API поддерживает полный CRUD для записей о вакцинации:

* получение списка вакцинаций с пагинацией (`skip`/`limit`, максимум 20 записей за раз);
* получение вакцинации по ID;
* создание новой записи;
* полное обновление записи через `PUT`;
* частичное обновление через `PATCH`;
* удаление записи;
* валидация входных данных;
* проверка связанных дат — согласована между Pydantic-валидатором и сервисным слоем, оба пути отдают `422`,
  даже если в `PATCH` передано только одно из двух связанных полей;
* обработка отсутствующих записей.

### Authentication

Для защиты API используется JWT-аутентификация с интеграцией **Keycloak**.

Приложение:

* получает JWT из `Authorization: Bearer <token>`;
* проверяет подпись JWT;
* получает OIDC-конфигурацию и JWKS от Keycloak асинхронно (`httpx.AsyncClient`),
  не блокируя обработку остальных запросов;
* кэширует OIDC-конфигурацию и публичные ключи в памяти процесса и умеет
  самостоятельно обновлять кэш при ротации ключей на стороне Keycloak;
* определяет текущего пользователя по JWT;
* связывает локального пользователя с идентификатором из Keycloak;
* ограничивает доступ к вакцинациям текущего пользователя.

### 🧪 Testing

Проект содержит автоматизированные API-тесты на:

* создание вакцинации;
* получение вакцинаций, включая границы пагинации;
* обновление, частичное обновление и связанную с ним валидацию дат;
* удаление;
* валидацию входных данных;
* обработку ошибок;
* работу пользователей;
* изоляцию данных между пользователями;
* проверку JWT: валидный токен, истёкший срок действия, неверные `audience`/`issuer`, поддельная подпись,
  неизвестный `kid`, самовосстановление кэша ключей при ротации.

Для тестов используется отдельная SQLite database, dependency overrides FastAPI, а для тестов авторизации —
самостоятельно сгенерированная тестовая RSA-пара ключей вместо реального Keycloak.

### Development

Проект поддерживает запуск в Docker и автоматический запуск тестов через GitHub Actions.

---

## 🛠 Стек технологий

| Technology     | Purpose                   |
|----------------|---------------------------|
| Python 3.13    | Основной язык             |
| FastAPI        | REST API framework        |
| Pydantic       | Валидация и схемы данных  |
| SQLAlchemy 2.x | ORM                       |
| SQLite         | База данных               |
| aiosqlite      | Асинхронный SQLite driver |
| Uvicorn        | ASGI server               |
| PyJWT          | Работа с JWT              |
| HTTPX          | HTTP-клиент               |
| Pytest         | Тестирование              |
| pytest-asyncio | Асинхронные тесты         |
| Docker         | Контейнеризация           |
| GitHub Actions | CI                        |

---

## Структура проекта

Проект построен с разделением ответственности между слоями:

```text
FastAPI_vaccines/
│
├── app_vaccines/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   └── keycloak.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── db_models.py
│   │   ├── repository.py
│   │   └── schemas.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── depends.py
│   │   ├── users.py
│   │   └── vaccines.py
│   │
│   └── main.py
│
├── tests/
│   ├── api_test.py
│   ├── config.py
│   ├── conftest.py
│   ├── test_auth_keycloak.py
│   ├── test_users.py
│   ├── test_vaccines.py
│   ├── test_vaccines_create.py
│   ├── test_vaccines_delete.py
│   ├── test_vaccines_isolation.py
│   ├── test_vaccines_read.py
│   └── test_vaccines_update.py
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

---

## Архитектура приложения

Приложение разделено на несколько логических компонентов:

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

---

## Модель данных

Основная сущность приложения — `Vaccine`.

Запись содержит информацию о вакцинации и принадлежит конкретному пользователю.

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

---

## 🔌 API Endpoints

### Vaccinations

Все endpoints вакцинаций требуют авторизации.

| Method   | Endpoint                 | Description                                                                                                                     |
|----------|--------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| `GET`    | `/vaccines`              | Возвращает список вакцинаций текущего пользователя                                                                              |
| `GET`    | `/vaccines/{vaccine_id}` | Получить вакцинацию по ID. Если запись не существует или принадлежит другому пользователю, она недоступна текущему пользователю |
| `POST`   | `/vaccines`              | Создаёт новую запись вакцинации для текущего пользователя                                                                       |
| `PUT`    | `/vaccines/{vaccine_id}` | Полностью обновить вакцинацию                                                                                                   |
| `PATCH`  | `/vaccines/{vaccine_id}` | Позволяет изменить только необходимые поля                                                                                      |
| `DELETE` | `/vaccines/{vaccine_id}` | Удалить вакцинацию текущего пользователя                                                                                        |

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

| Method | Endpoint    | Description                           |
|--------|-------------|---------------------------------------|
| `GET`  | `/users/me` | Получить данные текущего пользователя |
| `Post` | `/users/me` | Создание нового пользователя          |

---

# 🔐 Аутентификация

API использует Bearer JWT authentication.

Приложение получает OIDC configuration и JWKS от Keycloak асинхронно (через `httpx.AsyncClient`, без блокировки event
loop) и использует их для проверки подписи, `audience` и `issuer` каждого JWT.

OIDC-конфигурация и публичные ключи кэшируются в памяти процесса, чтобы не ходить в Keycloak на каждый запрос. При
ротации ключей на стороне Keycloak (появление нового `kid`, которого ещё нет в кэше) приложение самостоятельно обновляет
кэш, не отклоняя валидные токены.

# База данных

В текущей версии используется **SQLite**.

Работа с базой данных построена на:

* SQLAlchemy 2.x;
* `AsyncEngine`;
* `AsyncSession`;
* `aiosqlite`;
* SQLAlchemy ORM;
* Repository pattern

Работа с database выполняется асинхронно.

---

# Тестирование

🧪 Testing

Для запуска тестов: `pytest`

Тесты используют:

* pytest
* pytest-asyncio
* httpx
* тестовую SQLite database

Тестовые сценарии разделены по CRUD-операциям:

```text
tests/
├── config.py
├── conftest.py
├── test_auth_keycloak.py
├── test_users.py
├── test_vaccines.py
├── test_vaccines_create.py
├── test_vaccines_isolation.py
├── test_vaccines_read.py
├── test_vaccines_update.py
└── test_vaccines_delete.py
```

Проверяются основные позитивные и негативные сценарии API, включая обработку отсутствующих ресурсов и валидацию данных.

Отдельно, в `test_auth_keycloak.py`, проверяется логика проверки JWT (`app_vaccines/auth/keycloak.py`) без обращения к
реальному Keycloak: тесты сами генерируют RSA-ключи, подписывают ими тестовые токены и подменяют сетевые вызовы
`httpx.AsyncClient`, чтобы проверить валидные и невалидные токены (истёкший срок, чужая подпись, неверные `audience`/
`issuer`, неизвестный `kid`), а также самовосстановление кэша ключей при ротации.

---

# Планируемые улучшения

* поиск по заболеванию;
* фильтрация и сортировка;
* PostgreSQL;
* Alembic migrations;
* явный `response_model` для `/users/me` вместо сырого payload из токена;
* линтер и mypy в CI;
* увеличение test coverage и coverage-отчёт;
* увеличение test coverage;
* улучшение OpenAPI examples;
* production-ready configuration;
* улучшение Docker setup.

---

## 🎯 Project Goals

Проект создан как pet-проект для практики:

* разработки REST API на FastAPI;
* асинхронного программирования на Python;
* работы с SQLAlchemy 2.x;
* проектирования Repository / Service layer;
* API testing;
* pytest и async testing;
* Docker;
* CI/CD;
* JWT-based authentication;
* подготовки backend-проекта для QA Automation portfolio.

---

## 👩‍💻 Author

**Kseniya Dobina**

---

## 📄 License

Проект создан в учебных целях.
