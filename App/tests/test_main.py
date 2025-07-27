import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    # Test the root endpoint "/"
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue"}

def test_predict_endpoint():
    # Test the predict endpoint "/predict"
    response = client.post("/predict", json={"step": 1, "start_date": "2024-04-10 00:00:00", "end_date": "2024-04-10 12:00:00"})
    assert response.status_code == 200
    assert "predictions" in response.json()

def test_get_predictions_endpoint():
    # Test the get_predictions endpoint "/predictions"
    response = client.get("/predictions")
    assert response.status_code == 200
    assert "predictions" in response.json()
