import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
from datetime import datetime
import pika
import json

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def wait_for_rabbitmq():
    max_retries = 30
    attempt = 0
    
    while attempt < max_retries:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=os.getenv('RABBITMQ_HOST', 'rabbitmq-service'),
                    port=int(os.getenv('RABBITMQ_PORT', '5672')),
                    credentials=pika.PlainCredentials(
                        os.getenv('RABBITMQ_USER', 'guest'),
                        os.getenv('RABBITMQ_PASSWORD', 'guest')
                    )
                )
            )
            connection.close()
            logger.info("Successfully connected to RabbitMQ")
            return
        except Exception as e:
            attempt += 1
            logger.warning(f"RabbitMQ connection attempt {attempt}/{max_retries} failed: {str(e)}")
            if attempt == max_retries:
                logger.error("Could not connect to RabbitMQ after maximum retries")
                raise Exception("Could not connect to RabbitMQ")
            time.sleep(2)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    wait_for_rabbitmq()

@app.get("/health")
async def health_check():
    try:
        # Проверяем подключение к RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=os.getenv('RABBITMQ_HOST', 'rabbitmq-service'),
                port=int(os.getenv('RABBITMQ_PORT', '5672')),
                credentials=pika.PlainCredentials(
                    os.getenv('RABBITMQ_USER', 'guest'),
                    os.getenv('RABBITMQ_PASSWORD', 'guest')
                )
            )
        )
        connection.close()
        return {"status": "healthy", "rabbitmq": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vehicle-data/")
async def receive_vehicle_data(data: dict):
    try:
        # Подключение к RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=os.getenv('RABBITMQ_HOST', 'rabbitmq-service'),
                port=int(os.getenv('RABBITMQ_PORT', '5672')),
                credentials=pika.PlainCredentials(
                    os.getenv('RABBITMQ_USER', 'guest'),
                    os.getenv('RABBITMQ_PASSWORD', 'guest')
                )
            )
        )
        channel = connection.channel()
        
        # Создание очереди
        channel.queue_declare(queue='vehicle_data', durable=True)
        
        # Отправка сообщения в очередь как есть
        channel.basic_publish(
            exchange='',
            routing_key='vehicle_data',
            body=json.dumps(data)
        )
        
        connection.close()
        logger.info(f"Raw vehicle data sent to queue")
        return {"status": "success", "message": "Data sent to processing queue"}
    except Exception as e:
        logger.error(f"Error sending data to queue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
