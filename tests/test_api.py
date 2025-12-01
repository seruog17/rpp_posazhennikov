import pytest
from app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()

def test_create_sub():
    with app.test_client() as client:
        res = client.post("/subscription", json={
            "user_id": 1,
            "name": "Netflix",
            "amount": 300,
            "period": "monthly",
            "start_date": "2025-01-01"
        })
        assert res.status_code == 200

def test_get_subscriptions():
    with app.test_client() as client:
        res = client.get("/subscriptions")
        assert res.status_code == 200

def test_index():
    with app.test_client() as client:
        res = client.get("/")
        assert res.status_code == 200
        assert b"Subscriptions API is running!" in res.data

def test_delete_subscription():
    with app.test_client() as client:
        res = client.delete("/subscription/999")
        assert res.status_code == 200

def test_update_subscription():
    with app.test_client() as client:
        res = client.put("/subscription/999", json={"amount": 400})
        assert res.status_code == 200