import json
from app import app

client = app.test_client()

def test_create_sub():
    res = client.post("/subscription", json={
        "user_id": 1,
        "name": "Netflix",
        "amount": 300,
        "period": "monthly",
        "start_date": "2025-01-01"
    })
    assert res.status_code == 200
