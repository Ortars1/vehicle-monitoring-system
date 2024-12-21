import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    return TestClient(app)

@patch('main.pika.BlockingConnection')
def test_receive_vehicle_data(mock_connection, client):
    mock_channel = MagicMock()
    mock_connection.return_value.channel.return_value = mock_channel

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
    mock_channel.queue_declare.assert_called_once_with(queue='vehicle_data')
    mock_channel.basic_publish.assert_called_once()
