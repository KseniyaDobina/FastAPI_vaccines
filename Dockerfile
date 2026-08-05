# Используем официальный образ Python
FROM python:3.13-slim

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
CMD ["uvicorn", "app_vaccines.main:app", "--host", "0.0.0.0", "--port", "8000"]
# http://127.0.0.1:8000/docs запустится тут