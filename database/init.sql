CREATE TABLE vehicle_data (
    id SERIAL PRIMARY KEY,
    vehicle_id VARCHAR(50) NOT NULL,
    latitude DECIMAL(10, 6) NOT NULL,
    longitude DECIMAL(10, 6) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    speed DECIMAL(5, 2) NOT NULL,
    fuel_level DECIMAL(5, 2) NOT NULL,
    UNIQUE(vehicle_id, timestamp)
);
