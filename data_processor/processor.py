import pika
import json
import psycopg2
import logging
import time
import os
from datetime import datetime
from pydantic import BaseModel, validator, ValidationError
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Модель для валидации данных
class VehicleData(BaseModel):
    vehicle_id: str
    latitude: float
    longitude: float
    timestamp: datetime
    speed: float
    fuel_level: float

    @validator('vehicle_id')
    def validate_vehicle_id(cls, v):
        if not v or not isinstance(v, str) or len(v) > 50:
            raise ValueError('Invalid vehicle_id')
        return v

    @validator('latitude')
    def validate_latitude(cls, v):
        if not isinstance(v, (int, float)) or v < -90 or v > 90:
            raise ValueError('Invalid latitude')
        return float(v)

    @validator('longitude')
    def validate_longitude(cls, v):
        if not isinstance(v, (int, float)) or v < -180 or v > 180:
            raise ValueError('Invalid longitude')
        return float(v)

    @validator('speed')
    def validate_speed(cls, v):
        if not isinstance(v, (int, float)) or v < 0 or v > 300:  # максимальная скорость в км/ч
            raise ValueError('Invalid speed')
        return float(v)

    @validator('fuel_level')
    def validate_fuel_level(cls, v):
        if not isinstance(v, (int, float)) or v < 0 or v > 100:  # процент топлива
            raise ValueError('Invalid fuel level')
        return float(v)

def connect_to_rabbitmq():
    while True:
        try:
            credentials = pika.PlainCredentials(
                os.getenv('RABBITMQ_USER', 'guest'),
                os.getenv('RABBITMQ_PASS', 'guest')
            )
            parameters = pika.ConnectionParameters(
                host=os.getenv('RABBITMQ_HOST', 'rabbitmq-service'),
                port=int(os.getenv('RABBITMQ_PORT', 5672)),
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            return pika.BlockingConnection(parameters)
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            time.sleep(5)

def connect_to_db():
    while True:
        try:
            return psycopg2.connect(
                host=os.getenv('POSTGRES_HOST', 'database-service'),
                port=int(os.getenv('POSTGRES_PORT', 5432)),
                database=os.getenv('POSTGRES_DB', 'vehicle_monitoring'),
                user=os.getenv('POSTGRES_USER', 'postgres'),
                password=os.getenv('POSTGRES_PASSWORD', 'your_password')
            )
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            time.sleep(5)

def process_message(ch, method, properties, body):
    try:
        # Парсинг JSON
        raw_data = json.loads(body)
        logger.info(f"Received message: {raw_data}")

        # Валидация данных через Pydantic
        try:
            # Преобразование строки timestamp в datetime если необходимо
            if isinstance(raw_data.get('timestamp'), str):
                raw_data['timestamp'] = datetime.fromisoformat(raw_data['timestamp'].replace('Z', '+00:00'))
            
            validated_data = VehicleData(**raw_data)
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            # Отклоняем сообщение без повторной обработки
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return
        except Exception as e:
            logger.error(f"Data parsing error: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        # Подключение к БД и сохранение данных
        conn = connect_to_db()
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT INTO vehicle_data 
                    (vehicle_id, latitude, longitude, timestamp, speed, fuel_level)
                VALUES 
                    (%(vehicle_id)s, %(latitude)s, %(longitude)s, %(timestamp)s, %(speed)s, %(fuel_level)s)
                ON CONFLICT (vehicle_id, timestamp) 
                DO UPDATE SET 
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    speed = EXCLUDED.speed,
                    fuel_level = EXCLUDED.fuel_level;
            """, validated_data.dict())

            conn.commit()
            logger.info(f"Successfully processed message for vehicle {validated_data.vehicle_id}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            logger.error(f"Database error: {e}")
            conn.rollback()
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        finally:
            cur.close()
            conn.close()

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        if not ch.is_closed:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def main():
    while True:
        try:
            connection = connect_to_rabbitmq()
            channel = connection.channel()

            channel.queue_declare(queue='vehicle_data', durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(
                queue='vehicle_data',
                on_message_callback=process_message
            )

            logger.info("Starting to consume messages...")
            channel.start_consuming()

        except Exception as e:
            logger.error(f"Connection error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
