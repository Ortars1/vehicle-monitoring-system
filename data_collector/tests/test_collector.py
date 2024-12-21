import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_receive_vehicle_data():
    response = client.post(
        "/vehicle-data/",
        json={
            "vehicle_id": "TEST001",
            "latitude": 55.75,
            "longitude": 37.61,
            "timestamp": "2024-12-19T12:00:00",
            "speed": 60.5,
            "fuel_level": 75.0
        }
    )
    assert response.status_code == 200
