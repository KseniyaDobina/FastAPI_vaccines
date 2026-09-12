# Test Cases

Всего	138

## GET /vaccines

### Получение списка вакцинаций

| ID      | Название теста                             | Сценарий                                  | Ожидаемый результат                      | Статус |
|---------|--------------------------------------------|-------------------------------------------|------------------------------------------|--------|
| VAC-001 | `test_get_all_vaccines`                    | Получение списка всех вакцинаций          | `200`, ответ является списком            | ✅     |
| VAC-002 | `test_get_all_vaccines_default_pagination` | Получение списка без параметров пагинации | `200`, используются `skip=0`, `limit=10` | ✅     |

### Получение вакцинации по ID

| ID      | Название теста               | Сценарий                                | Ожидаемый результат                              | Статус |
|---------|------------------------------|-----------------------------------------|--------------------------------------------------|--------|
| VAC-003 | `test_get_vaccine`           | Получение существующей вакцинации по ID | `200`, возвращаются корректные данные вакцинации | ✅     |
| VAC-004 | `test_get_vaccine_not_found` | Получение несуществующей вакцинации     | `404`, `Данные о вакцинации не найдены`          | ✅     |

### Параметр `limit`

| ID      | Название теста                                      | Сценарий                                 | Значение | Ожидаемый результат | Статус |
|---------|-----------------------------------------------------|------------------------------------------|---------:|---------------------|--------|
| VAC-005 | `test_get_all_vaccines_accepts_limit_within_bounds` | Допустимое минимальное значение `limit`  |      `1` | `200`               | ✅     |
| VAC-006 | `test_get_all_vaccines_accepts_limit_within_bounds` | Допустимое максимальное значение `limit` |     `20` | `200`               | ✅     |
| VAC-007 | `test_get_all_vaccines_rejects_limit_out_of_bounds` | `limit` меньше минимального              |     `-1` | `422`               | ✅     |
| VAC-008 | `test_get_all_vaccines_rejects_limit_out_of_bounds` | `limit` равен `0`                        |      `0` | `422`               | ✅     |
| VAC-009 | `test_get_all_vaccines_rejects_limit_out_of_bounds` | `limit` больше максимального             |     `21` | `422`               | ✅     |
| VAC-010 | `test_get_all_vaccines_rejects_limit_out_of_bounds` | Значительно превышенное значение `limit` |   `1000` | `422`               | ✅     |

### Параметр `skip`

| ID      | Название теста                                | Сценарий                               | Значение | Ожидаемый результат | Статус |
|---------|-----------------------------------------------|----------------------------------------|---------:|---------------------|--------|
| VAC-011 | `test_get_all_vaccines_accepts_skip_zero`     | Допустимое минимальное значение `skip` |      `0` | `200`               | ✅     |
| VAC-012 | `test_get_all_vaccines_rejects_negative_skip` | Отрицательный `skip`                   |     `-1` | `422`               | ✅     |
| VAC-013 | `test_get_all_vaccines_rejects_negative_skip` | Отрицательный `skip`                   |   `-100` | `422`               | ✅     |

## POST /vaccines

### Создание вакцинации

| ID      | Название теста                                  | Сценарий                     | Ожидаемый результат   | Статус |
|---------|-------------------------------------------------|------------------------------|-----------------------|--------|
| VAC-014 | `test_create_vaccine_without_body`              | POST без тела                | `422`                 | ✅     |
| VAC-015 | `test_create_vaccine`                           | Создание с валидными данными | `201`                 | ✅     |
| VAC-016 | `test_create_vaccine_without_notes`             | Создание без `notes`         | `201`, `notes = null` | ✅     |
| VAC-017 | `test_create_vaccine_with_null_expiration_date` | `expiration_date = null`     | `201`                 | ✅     |

### POST /vaccines — валидация длины полей

| ID      | Название теста                                 | Сценарий                                                                      | Параметры                                                                                                                                                                      | Кол-во pytest-тестов | Ожидаемый результат                                                     |
|---------|------------------------------------------------|-------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------:|-------------------------------------------------------------------------|
| VAC-003 | `test_create_vaccine_min_length_validation`    | Проверка минимально допустимой длины строковых полей при создании вакцинации  | `disease=ab`<br>`vaccine_name=ab`<br>`dose_number=""`<br>`type_vaccine=""`<br>`lot=""`<br>`manufacturer=a`<br>`clinic=ab`<br>`country=a`<br>`city=a`                           |                **9** | Для каждого поля API возвращает `422`                                   |
| VAC-004 | `test_create_vaccine_max_length_validation`    | Проверка максимально допустимой длины строковых полей при создании вакцинации | `disease=101`<br>`vaccine_name=101`<br>`dose_number=31`<br>`type_vaccine=101`<br>`lot=101`<br>`manufacturer=101`<br>`clinic=201`<br>`country=101`<br>`city=101`<br>`notes=301` |               **10** | Для каждого поля API возвращает `422`                                   |
| VAC-005 | `test_create_vaccine_invalid_date`             | Проверка некорректных форматов дат                                            | `vaccination_date=not-a-date`<br>`vaccination_date=20.08.2026`<br>`vaccination_date=2026/08/20`<br>`expiration_date=not-a-date`<br>`expiration_date=31.01.2027`                |                **5** | Для каждого варианта API возвращает `422`                               |
| VAC-006 | `test_create_vaccine_required_fields`          | Проверка обязательности полей                                                 | `disease`<br>`vaccine_name`<br>`dose_number`<br>`vaccination_date`<br>`type_vaccine`<br>`lot`<br>`manufacturer`<br>`clinic`<br>`country`<br>`city`                             |               **10** | При отсутствии каждого обязательного поля API возвращает `422`          |
| VAC-007 | `test_create_vaccine_none_for_required_fields` | Проверка запрета `None` для обязательных полей                                | `disease`<br>`vaccine_name`<br>`dose_number`<br>`vaccination_date`<br>`type_vaccine`<br>`lot`<br>`manufacturer`<br>`clinic`<br>`country`<br>`city`                             |               **10** | При передаче `None` для каждого обязательного поля API возвращает `422` |

### Валидация дат

| ID      | Название теста                                 | Поле               | Значение     | Ожидаемый результат | Статус |
|---------|------------------------------------------------|--------------------|--------------|---------------------|--------|
| VAC-021 | `test_create_vaccine_invalid_vaccination_date` | `vaccination_date` | `not-a-date` | `422`               | ✅     |
| VAC-022 | `test_create_vaccine_invalid_vaccination_date` | `vaccination_date` | `20.08.2026` | `422`               | ✅     |

## PUT /vaccines/{id}

### Полное обновление вакцинации

| ID      | Название теста               | Сценарий                                  | Ожидаемый результат                             | Статус |
|---------|------------------------------|-------------------------------------------|-------------------------------------------------|--------|
| VAC-023 | `test_put_vaccine`           | Полное обновление существующей вакцинации | `200`, возвращаются обновлённые данные          | ✅     |
| VAC-024 | `test_put_vaccine`           | Проверка обновления записи в БД после PUT | Все переданные поля действительно изменены в БД | ✅     |
| VAC-025 | `test_put_vaccine_not_found` | Обновление несуществующей вакцинации      | `404`, `Данные о вакцинации не найдены`         | ✅     |

---

## PATCH /vaccines/{id}

### Частичное обновление

| ID      | Название теста                       | Сценарий                                                           | Ожидаемый результат                                          | Статус |
|---------|--------------------------------------|--------------------------------------------------------------------|--------------------------------------------------------------|--------|
| VAC-026 | `test_patch_vaccine`                 | Частичное обновление одного поля (`city`)                          | `200`, `city` изменён                                        | ✅     |
| VAC-027 | `test_patch_vaccine`                 | Проверка сохранения остальных полей при изменении одного поля      | Остальные поля остаются без изменений                        | ✅     |
| VAC-028 | `test_patch_vaccine`                 | Проверка частичного обновления в БД                                | Изменённое поле сохранено в БД, остальные поля не изменились | ✅     |
| VAC-029 | `test_patch_vaccine_multiple_fields` | Частичное обновление нескольких полей (`city`, `clinic`)           | `200`, оба поля изменены                                     | ✅     |
| VAC-030 | `test_patch_vaccine_multiple_fields` | Проверка сохранения остальных полей при изменении нескольких полей | Остальные поля остаются без изменений                        | ✅     |
| VAC-031 | `test_patch_vaccine_not_found`       | Частичное обновление несуществующей вакцинации                     | `404`, `Данные о вакцинации не найдены`                      | ✅     |

### Минимальная длина строк

| ID      | Название теста                               | Поле           | Значение | Ожидаемый результат | Статус |
|---------|----------------------------------------------|----------------|----------|---------------------|--------|
| VAC-032 | `test_patch_rejects_too_short_string_fields` | `disease`      | `ab`     | `422`               | ✅     |
| VAC-033 | `test_patch_rejects_too_short_string_fields` | `vaccine_name` | `ab`     | `422`               | ✅     |
| VAC-034 | `test_patch_rejects_too_short_string_fields` | `dose_number`  | `""`     | `422`               | ✅     |
| VAC-035 | `test_patch_rejects_too_short_string_fields` | `type_vaccine` | `""`     | `422`               | ✅     |
| VAC-036 | `test_patch_rejects_too_short_string_fields` | `lot`          | `""`     | `422`               | ✅     |
| VAC-037 | `test_patch_rejects_too_short_string_fields` | `manufacturer` | `a`      | `422`               | ✅     |
| VAC-038 | `test_patch_rejects_too_short_string_fields` | `clinic`       | `ab`     | `422`               | ✅     |
| VAC-039 | `test_patch_rejects_too_short_string_fields` | `country`      | `a`      | `422`               | ✅     |
| VAC-040 | `test_patch_rejects_too_short_string_fields` | `city`         | `a`      | `422`               | ✅     |
| VAC-041 | `test_patch_rejects_too_short_string_fields` | `notes`        | `""`     | `422`               | ✅     |

### Максимальная длина строк

| ID      | Название теста                              | Поле           | Значение   | Ожидаемый результат | Статус |
|---------|---------------------------------------------|----------------|------------|---------------------|--------|
| VAC-042 | `test_patch_rejects_too_long_string_fields` | `disease`      | 101 символ | `422`               | ✅     |
| VAC-043 | `test_patch_rejects_too_long_string_fields` | `vaccine_name` | 101 символ | `422`               | ✅     |
| VAC-044 | `test_patch_rejects_too_long_string_fields` | `dose_number`  | 31 символ  | `422`               | ✅     |
| VAC-045 | `test_patch_rejects_too_long_string_fields` | `type_vaccine` | 101 символ | `422`               | ✅     |
| VAC-046 | `test_patch_rejects_too_long_string_fields` | `lot`          | 101 символ | `422`               | ✅     |
| VAC-047 | `test_patch_rejects_too_long_string_fields` | `manufacturer` | 101 символ | `422`               | ✅     |
| VAC-048 | `test_patch_rejects_too_long_string_fields` | `clinic`       | 201 символ | `422`               | ✅     |
| VAC-049 | `test_patch_rejects_too_long_string_fields` | `country`      | 101 символ | `422`               | ✅     |
| VAC-050 | `test_patch_rejects_too_long_string_fields` | `city`         | 101 символ | `422`               | ✅     |
| VAC-051 | `test_patch_rejects_too_long_string_fields` | `notes`        | 301 символ | `422`               | ✅     |

### Минимально допустимая длина строк

| ID      | Название теста                              | Поле           | Значение  | Ожидаемый результат | Статус |
|---------|---------------------------------------------|----------------|-----------|---------------------|--------|
| VAC-052 | `test_patch_accepts_minimum_string_lengths` | `disease`      | 3 символа | `200`               | ✅     |
| VAC-053 | `test_patch_accepts_minimum_string_lengths` | `vaccine_name` | 3 символа | `200`               | ✅     |
| VAC-054 | `test_patch_accepts_minimum_string_lengths` | `dose_number`  | 1 символ  | `200`               | ✅     |
| VAC-055 | `test_patch_accepts_minimum_string_lengths` | `type_vaccine` | 1 символ  | `200`               | ✅     |
| VAC-056 | `test_patch_accepts_minimum_string_lengths` | `lot`          | 1 символ  | `200`               | ✅     |
| VAC-057 | `test_patch_accepts_minimum_string_lengths` | `manufacturer` | 2 символа | `200`               | ✅     |
| VAC-058 | `test_patch_accepts_minimum_string_lengths` | `clinic`       | 3 символа | `200`               | ✅     |
| VAC-059 | `test_patch_accepts_minimum_string_lengths` | `country`      | 2 символа | `200`               | ✅     |
| VAC-060 | `test_patch_accepts_minimum_string_lengths` | `city`         | 2 символа | `200`               | ✅     |
| VAC-061 | `test_patch_accepts_minimum_string_lengths` | `notes`        | 1 символ  | `200`               | ✅     |

### Максимально допустимая длина строк

| ID      | Название теста                              | Поле           | Значение     | Ожидаемый результат | Статус |
|---------|---------------------------------------------|----------------|--------------|---------------------|--------|
| VAC-062 | `test_patch_accepts_maximum_string_lengths` | `disease`      | 100 символов | `200`               | ✅     |
| VAC-063 | `test_patch_accepts_maximum_string_lengths` | `vaccine_name` | 100 символов | `200`               | ✅     |
| VAC-064 | `test_patch_accepts_maximum_string_lengths` | `dose_number`  | 30 символов  | `200`               | ✅     |
| VAC-065 | `test_patch_accepts_maximum_string_lengths` | `type_vaccine` | 100 символов | `200`               | ✅     |
| VAC-066 | `test_patch_accepts_maximum_string_lengths` | `lot`          | 100 символов | `200`               | ✅     |
| VAC-067 | `test_patch_accepts_maximum_string_lengths` | `manufacturer` | 100 символов | `200`               | ✅     |
| VAC-068 | `test_patch_accepts_maximum_string_lengths` | `clinic`       | 200 символов | `200`               | ✅     |
| VAC-069 | `test_patch_accepts_maximum_string_lengths` | `country`      | 100 символов | `200`               | ✅     |
| VAC-070 | `test_patch_accepts_maximum_string_lengths` | `city`         | 100 символов | `200`               | ✅     |
| VAC-071 | `test_patch_accepts_maximum_string_lengths` | `notes`        | 300 символов | `200`               | ✅     |

### Валидация дат

| ID      | Название теста                                                        | Сценарий                                                                                       | Ожидаемый результат   | Статус |
|---------|-----------------------------------------------------------------------|------------------------------------------------------------------------------------------------|-----------------------|--------|
| VAC-072 | `test_patch_rejects_invalid_date_format`                              | Некорректный формат `vaccination_date`                                                         | `422`                 | ✅     |
| VAC-073 | `test_patch_rejects_invalid_date_format`                              | Некорректный формат `expiration_date`                                                          | `422`                 | ✅     |
| VAC-074 | `test_patch_rejects_expiration_date_before_existing_vaccination_date` | `expiration_date` раньше существующей `vaccination_date` при передаче только `expiration_date` | `422`                 | ✅     |
| VAC-075 | `test_patch_rejects_expiration_date_before_vaccination_date`          | `expiration_date` раньше `vaccination_date` при передаче обеих дат                             | `422`                 | ✅     |
| VAC-076 | `test_patch_rejects_equal_vaccination_and_expiration_dates`           | `expiration_date` равен `vaccination_date`                                                     | `422`                 | ✅     |
| VAC-077 | `test_patch_accepts_valid_dates`                                      | Валидные `vaccination_date` и `expiration_date`                                                | `200`, даты обновлены | ✅     |

## DELETE /vaccines/{id}

### Удаление вакцинации

| ID      | Название теста                  | Сценарий                                    | Ожидаемый результат                       | Статус |
|---------|---------------------------------|---------------------------------------------|-------------------------------------------|--------|
| VAC-078 | `test_delete_vaccine`           | Удаление существующей вакцинации            | `200`, возвращается сообщение об удалении | ✅     |
| VAC-079 | `test_delete_vaccine`           | Проверка фактического удаления записи из БД | Запись с указанным `id` отсутствует в БД  | ✅     |
| VAC-080 | `test_delete_vaccine`           | Получение удалённой вакцинации              | `404`                                     | ✅     |
| VAC-081 | `test_delete_vaccine_not_found` | Удаление вакцинации, которой не существует  | `404`, `Данные о вакцинации не найдены`   | ✅     |

## Authentication — отсутствие авторизации

| ID      | Название теста                         | Метод  | Endpoint         | Сценарий               | Ожидаемый результат                  |
|---------|----------------------------------------|--------|------------------|------------------------|--------------------------------------|
| VAC-082 | `test_vaccines_endpoints_without_auth` | GET    | `/vaccines`      | Запрос без авторизации | `401`, `detail: "Not authenticated"` |
| VAC-083 | `test_vaccines_endpoints_without_auth` | POST   | `/vaccines`      | Запрос без авторизации | `401`, `detail: "Not authenticated"` |
| VAC-084 | `test_vaccines_endpoints_without_auth` | GET    | `/vaccines/{id}` | Запрос без авторизации | `401`, `detail: "Not authenticated"` |
| VAC-085 | `test_vaccines_endpoints_without_auth` | PUT    | `/vaccines/{id}` | Запрос без авторизации | `401`, `detail: "Not authenticated"` |
| VAC-086 | `test_vaccines_endpoints_without_auth` | PATCH  | `/vaccines/{id}` | Запрос без авторизации | `401`, `detail: "Not authenticated"` |
| VAC-087 | `test_vaccines_endpoints_without_auth` | DELETE | `/vaccines/{id}` | Запрос без авторизации | `401`, `detail: "Not authenticated"` |

## Изоляция данных между пользователями

| ID      | Название теста                                  | Метод  | Endpoint         | Сценарий                                                  | Ожидаемый результат                                                                    |
|---------|-------------------------------------------------|--------|------------------|-----------------------------------------------------------|----------------------------------------------------------------------------------------|
| VAC-088 | `test_user_cannot_get_another_users_vaccine`    | GET    | `/vaccines/{id}` | Пользователь пытается получить чужую вакцинацию           | `404`, `detail: "Данные о вакцинации не найдены"`                                      |
| VAC-089 | `test_user_cannot_update_another_users_vaccine` | PUT    | `/vaccines/{id}` | Пользователь пытается полностью изменить чужую вакцинацию | `404`, `detail: "Данные о вакцинации не найдены"`; данные чужой вакцинации не изменены |
| VAC-090 | `test_user_cannot_patch_another_users_vaccine`  | PATCH  | `/vaccines/{id}` | Пользователь пытается частично изменить чужую вакцинацию  | `404`, `detail: "Данные о вакцинации не найдены"`; данные чужой вакцинации не изменены |
| VAC-091 | `test_user_cannot_delete_another_users_vaccine` | DELETE | `/vaccines/{id}` | Пользователь пытается удалить чужую вакцинацию            | `404`, `detail: "Данные о вакцинации не найдены"`; вакцинация не удаляется             |

## Keycloak / JWT-аутентификация

### Валидация JWT-токена

| ID     | Название теста                       | Сценарий                                                   | Ожидаемый результат                                                                        |
|--------|--------------------------------------|------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| KC-001 | `test_decode_token_valid`            | Декодирование валидного JWT-токена                         | Токен успешно декодируется; `sub` и `preferred_username` соответствуют ожидаемым значениям |
| KC-002 | `test_decode_token_expired`          | Декодирование просроченного токена                         | `HTTPException` со статусом `401`                                                          |
| KC-003 | `test_decode_token_wrong_audience`   | Токен с неправильным `aud`                                 | `HTTPException` со статусом `401`                                                          |
| KC-004 | `test_decode_token_wrong_issuer`     | Токен с неправильным `iss`                                 | `HTTPException` со статусом `401`                                                          |
| KC-005 | `test_decode_token_forged_signature` | Токен подписан чужим приватным ключом при корректном `kid` | Подпись отклоняется; `HTTPException` со статусом `401`                                     |
| KC-006 | `test_decode_token_unknown_kid`      | Токен с неизвестным `kid`                                  | `HTTPException` со статусом `401`; необработанного исключения нет                          |

### Кэширование OIDC/JWKS

| ID     | Название теста                             | Сценарий                           | Ожидаемый результат                                                             |
|--------|--------------------------------------------|------------------------------------|---------------------------------------------------------------------------------|
| KC-007 | `test_oidc_config_is_cached_between_calls` | Повторный запрос OIDC-конфигурации | Конфигурация запрашивается из сети только один раз; второй вызов использует кэш |

### Ротация ключей Keycloak

| ID     | Название теста                                                            | Сценарий                                           | Ожидаемый результат                                                                                                          |
|--------|---------------------------------------------------------------------------|----------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| KC-008 | `test_decode_token_self_heals_on_key_rotation`                            | Токен подписан новым ключом после ротации Keycloak | Кэш автоматически обновляется; новый токен успешно валидируется; новый ключ добавляется в кэш, старый ключ сохраняется       |
| KC-009 | `test_decode_token_retries_once_if_key_still_missing_after_first_refresh` | Новый ключ отсутствует при первом обновлении JWKS  | Выполняется повторное обновление JWKS; после появления ключа токен успешно валидируется; всего выполняется 2 запроса за JWKS |

## Users

### Отсутствие авторизации

| ID      | Название теста                      | Метод | Endpoint    | Сценарий                                               | Ожидаемый результат                  |
|---------|-------------------------------------|-------|-------------|--------------------------------------------------------|--------------------------------------|
| USR-001 | `test_users_endpoints_without_auth` | GET   | `/users/me` | Получение данных текущего пользователя без авторизации | `401`, `detail: "Not authenticated"` |
| USR-002 | `test_users_endpoints_without_auth` | POST  | `/users`    | Создание пользователя без авторизации                  | `401`, `detail: "Not authenticated"` |

### Получение данных текущего пользователя

| ID      | Название теста | Метод | Endpoint    | Сценарий                                               | Ожидаемый результат |
|---------|----------------|-------|-------------|--------------------------------------------------------|---------------------|
| USR-003 | `test_get_me`  | GET   | `/users/me` | Получение данных текущего авторизованного пользователя | `200`               |

### Создание пользователя

| ID      | Название теста                                | Метод | Endpoint | Сценарий                                                  | Ожидаемый результат                                                                           |
|---------|-----------------------------------------------|-------|----------|-----------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| USR-004 | `test_create_user_success`                    | POST  | `/users` | Успешное создание нового пользователя                     | `201`; в ответе корректные `username`, `email` и `id`; пользователь действительно создан в БД |
| USR-005 | `test_create_user_conflict_if_already_exists` | POST  | `/users` | Попытка создать пользователя, который уже существует в БД | `409`, `detail: "Пользователь уже создан"`                                                    |
