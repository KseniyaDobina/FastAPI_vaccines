# Используем официальный образ Python
FROM python:3.14-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Открываем порт FastAPI
EXPOSE 8000

# Запускаем приложение
CMD alembic upgrade head && exec uvicorn app_vaccines.main:app --host 0.0.0.0 --port 8000
