import os
from flask import Flask, request, jsonify
from migrator import run_migrations
import psycopg2
from datetime import datetime, timedelta

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sub_user:sub_pass@localhost:5432/subscriptions_db")

run_migrations()

def get_conn():
    return psycopg2.connect(DATABASE_URL)

@app.route('/')
def index():
    return "Subscriptions API is running!"

@app.route('/subscription', methods=['POST'])
def create_subscription():
    data = request.json
    user_id = data['user_id']
    name = data['name']
    amount = data['amount']
    period = data['period']
    start_date = data['start_date']

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO subscriptions (user_id, name, amount, period, start_date, next_payment)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
    """, (user_id, name, amount, period, start_date, start_date))
    sub_id = cur.fetchone()[0]
    cur.execute("INSERT INTO audit_log (subscription_id, action, action_date) VALUES (%s, %s, %s)",
                (sub_id, 'create', datetime.now()))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status":"created", "subscription_id": sub_id})

@app.route('/subscriptions', methods=['GET'])
def get_subscriptions():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, name, amount, period, start_date, next_payment FROM subscriptions")
    subs = cur.fetchall()
    cur.close()
    conn.close()
    result = []
    for s in subs:
        result.append({
            "id": s[0],
            "user_id": s[1],
            "name": s[2],
            "amount": float(s[3]),
            "period": s[4],
            "start_date": s[5].strftime("%Y-%m-%d"),
            "next_payment": s[6].strftime("%Y-%m-%d")
        })
    return jsonify(result)

@app.route('/subscription/<int:sub_id>', methods=['PUT'])
def update_subscription(sub_id):
    data = request.json
    conn = get_conn()
    cur = conn.cursor()
    if 'amount' in data:
        cur.execute("UPDATE subscriptions SET amount=%s WHERE id=%s", (data['amount'], sub_id))
    if 'period' in data:
        cur.execute("UPDATE subscriptions SET period=%s WHERE id=%s", (data['period'], sub_id))
    if 'next_payment' in data:
        cur.execute("UPDATE subscriptions SET next_payment=%s WHERE id=%s", (data['next_payment'], sub_id))
    cur.execute("INSERT INTO audit_log (subscription_id, action, action_date) VALUES (%s, %s, %s)",
                (sub_id, 'update', datetime.now()))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status":"updated"})

@app.route('/subscription/<int:sub_id>', methods=['DELETE'])
def delete_subscription(sub_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM subscriptions WHERE id=%s", (sub_id,))
    cur.execute("INSERT INTO audit_log (subscription_id, action, action_date) VALUES (%s, %s, %s)",
                (sub_id, 'delete', datetime.now()))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status":"deleted"})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8000)
