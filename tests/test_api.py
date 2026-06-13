from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.main import app

client=TestClient(app)

def test_health_check():
    response=client.get("/")
    assert response.status_code==200
    assert response.json()["status"]=="Fraud Detection API is running"

def test_login():
    response=client.post("/token", data={
        "username": "admin",
        "password": "secret123"
    })
    assert response.status_code==200
    assert "access_token" in response.json()

def test_predict_without_token():
    response=client.post("/predict", json={
        "transaction_amount":450.0,
        "transaction_hour":2,
        "days_since_last_transaction":1,
        "customer_age":29,
        "is_foreign_transaction":1,
        "num_transactions_today":15
    })
    assert response.status_code==401

def test_predict_with_token():
    login=client.post("/token", data={
        "username":"admin",
        "password":"secret123"
    })
    token=login.json()["access_token"]

    response=client.post("/predict",
        json={
            "transaction_amount": 450.0,
            "transaction_hour": 2,
            "days_since_last_transaction": 1,
            "customer_age": 29,
            "is_foreign_transaction": 1,
            "num_transactions_today": 15
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code==200
    assert "verdict" in response.json()
    assert "fraud_probability" in response.json()