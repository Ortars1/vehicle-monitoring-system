# ./data_collector/Dockerfile
FROM python:3.9-slim

# Установка зависимостей для psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Установка pytest
RUN pip install pytest

# Копирование исходного кода
COPY . .

# Команда для запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
