import pytest
from app import app
import json
import psycopg2

@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()

@pytest.fixture
def setup_db():
    DATABASE_URL = "postgresql://sub_user:sub_pass@localhost:5432/subscriptions_db"
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    cur.execute("DELETE FROM audit_log")
    cur.execute("DELETE FROM subscriptions")
    cur.execute("DELETE FROM users")
    
    cur.execute("INSERT INTO users (id, name) VALUES (1, 'Test User')")
    
    conn.commit()
    cur.close()
    conn.close()

def test_create_sub(client, setup_db):
    res = client.post("/subscription", json={
        "user_id": 1,
        "name": "Netflix",
        "amount": 300,
        "period": "monthly",
        "start_date": "2025-01-01"
    })
    assert res.status_code == 200

def test_get_subscriptions(client, setup_db):
    res = client.get("/subscriptions")
    assert res.status_code == 200

def test_index(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Subscriptions API is running!" in res.data

def test_delete_subscription(client, setup_db):
    res = client.delete("/subscription/999")
    assert res.status_code == 200

def test_update_subscription(client, setup_db):
    res = client.put("/subscription/999", json={"amount": 400})
    assert res.status_code == 200