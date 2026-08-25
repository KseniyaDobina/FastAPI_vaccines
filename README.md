# 💉 Vaccines API

> REST API для ведения личного журнала вакцинации.

Во многих медицинских учреждениях информация о ранее сделанных прививках хранится в разных системах или вовсе теряется при смене поликлиники. Цель проекта — создать простой REST API для хранения собственной истории вакцинации.

Проект создан в учебных целях для изучения FastAPI и автоматизированного тестирования API. Приложение позволяет создавать, получать, изменять и удалять записи о вакцинации.

> ⚠️ Важно:
> API не связано с государственными или частными медицинскими учреждениями.
> Все данные вводятся пользователем вручную и не проверяются через системы ОМС, ДМС или другие медицинские сервисы.

---

## ✨ Возможности

### Vaccinations

* Получение списка вакцинаций `GET`
* Получение вакцинации по `id`
* Создание записи о вакцинации `POST`
* Полное обновление записи через `PUT`
* Частичное обновление через `PATCH`
* Удаление записи `DELETE`
* Валидация входных данных через Pydantic
* Обработка ошибок `404 Not Found`

### Authentication

* Работа с авторизацией пользователя
* Получение текущего пользователя через защищённый endpoint
* JWT / Keycloak integration

### Development & QA

* Асинхронная работа с SQLite
* SQLAlchemy 2.x
* Repository / Service layer
* Docker
* Автоматизированные API-тесты
* GitHub Actions CI
* Swagger / OpenAPI documentation


---

## 🛠 Стек технологий

| Technology     | Purpose                   |
| -------------- | ------------------------- |
| Python 3.13    | Основной язык             |
| FastAPI        | REST API                  |
| Pydantic       | Валидация и схемы данных  |
| SQLAlchemy 2.x | ORM                       |
| SQLite         | База данных               |
| aiosqlite      | Асинхронный SQLite driver |
| Uvicorn        | ASGI server               |
| PyJWT          | Работа с JWT              |
| HTTPX          | HTTP-клиент для тестов    |
| Pytest         | Тестирование              |
| pytest-asyncio | Асинхронное тестирование  |
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
│   │   ├── .env.example
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
│   └── test_api.py
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── requirements.txt
└── README.md
```
---

## Архитектура приложения

Проект построен с разделением ответственности:

**`routers`**

HTTP endpoints и обработка запросов FastAPI.

**`schemas`**

Pydantic-модели для валидации входных и выходных данных.

**`db_models`**

SQLAlchemy ORM-модели базы данных.

**`repository`**

Работа с данными и операции над сущностями.

**`service`**

Бизнес-логика приложения.

**`auth`**

Компоненты авторизации и получения текущего пользователя.

**`database`**

Создание async engine и работа с `AsyncSession`.

---

## Модель данных

Модель вакцинации содержит информацию о заболевании, вакцине, дозе, датах вакцинации, производителе и месте проведения вакцинации.

### Fields

| Field              | Type      | Required | Description                             |
| ------------------ | --------- | :------: | --------------------------------------- |
| `id`               | `integer` |     —    | Уникальный идентификатор записи         |
| `disease`          | `string`  |     ✅    | Заболевание                             |
| `vaccine_name`     | `string`  |     ✅    | Название вакцины                        |
| `dose_number`      | `string`  |     ✅    | Номер дозы                              |
| `vaccination_date` | `date`    |     ✅    | Дата вакцинации                         |
| `expiration_date`  | `date`    |     ❌    | Дата окончания действия / срок годности |
| `type_vaccine`     | `string`  |     ✅    | Тип вакцины                             |
| `lot`              | `string`  |     ✅    | Номер партии                            |
| `manufacturer`     | `string`  |     ✅    | Производитель                           |
| `clinic`           | `string`  |     ✅    | Медицинская организация / клиника       |
| `country`          | `string`  |     ✅    | Страна                                  |
| `city`             | `string`  |     ✅    | Город                                   |
| `notes`            | `string`  |     ❌    | Дополнительные заметки                  |

---

## 🔌 API Endpoints

### Vaccinations

| Method   | Endpoint                 | Description                   |
| -------- | ------------------------ | ----------------------------- |
| `GET`    | `/vaccines`              | Получить список вакцинаций    |
| `GET`    | `/vaccines/{vaccine_id}` | Получить вакцинацию по ID     |
| `POST`   | `/vaccines`              | Создать вакцинацию            |
| `PUT`    | `/vaccines/{vaccine_id}` | Полностью обновить вакцинацию |
| `PATCH`  | `/vaccines/{vaccine_id}` | Частично обновить вакцинацию  |
| `DELETE` | `/vaccines/{vaccine_id}` | Удалить вакцинацию            |

### Users

| Method | Endpoint      | Description                           |
| ------ | ------------- | ------------------------------------- |
| `GET`  | `/users/user` | Получить данные текущего пользователя |

---

## База данных

В текущей версии используется **SQLite**.

Работа с базой данных построена на:

* SQLAlchemy Async Engine
* `AsyncSession`
* `aiosqlite`
* SQLAlchemy ORM
* Repository pattern

Основная ORM-модель вакцинации определена в `VaccineBase`. Она содержит `id` и 13 полей данных вакцинации.


---

## Тестирование

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
├── test_vaccines_create.py
├── test_vaccines_read.py
├── test_vaccines_update.py
└── test_vaccines_delete.py
```

Проверяются основные позитивные и негативные сценарии API, включая обработку отсутствующих ресурсов и валидацию данных.

---

## Планируемые улучшения

* [x] CRUD operations
* [x] Async SQLite
* [x] SQLAlchemy Repository / Service layer
* [x] PATCH endpoint
* [x] Docker
* [x] Automated API tests
* [x] GitHub Actions
* [x] Authentication foundation
* [ ] Полноценная авторизация пользователей
* [ ] Привязка вакцинаций к пользователю
* [ ] PostgreSQL
* [ ] Alembic migrations
* [ ] Полноценная пагинация
* [ ] Поиск по заболеванию
* [ ] Фильтрация и сортировка
* [ ] Расширение negative API tests
* [ ] Увеличение test coverage
* [ ] Улучшение OpenAPI response examples
* [ ] Production-ready configuration
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
