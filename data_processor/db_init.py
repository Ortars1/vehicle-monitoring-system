# db_init.py
import psycopg2
import os
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    retries = 30
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST', 'database-service'),
                port=int(os.getenv('POSTGRES_PORT', 5432)),
                database=os.getenv('POSTGRES_DB', 'vehicle_monitoring'),
                user=os.getenv('POSTGRES_USER', 'postgres'),
                password=os.getenv('POSTGRES_PASSWORD', 'your_password')
            )
            cur = conn.cursor()
            
            # Создание таблицы
            cur.execute("""
                CREATE TABLE IF NOT EXISTS vehicle_data (
                    id SERIAL PRIMARY KEY,
                    vehicle_id VARCHAR(50) NOT NULL,
                    latitude DECIMAL(10, 6) NOT NULL,
                    longitude DECIMAL(10, 6) NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    speed DECIMAL(5, 2) NOT NULL,
                    fuel_level DECIMAL(5, 2) NOT NULL,
                    UNIQUE(vehicle_id, timestamp)
                );
            """)
            
            conn.commit()
            cur.close()
            conn.close()
            logger.info("Database initialized successfully")
            break
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            retries -= 1
            time.sleep(2)
            
if __name__ == "__main__":
    init_db()
