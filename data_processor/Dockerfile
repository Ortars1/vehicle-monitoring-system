FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Добавляем инициализацию БД перед запуском основного процесса
CMD ["sh", "-c", "python db_init.py && python processor.py"]
