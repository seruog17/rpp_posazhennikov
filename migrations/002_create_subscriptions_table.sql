CREATE TABLE IF NOT EXISTS subscriptions(
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    name VARCHAR(100),
    amount FLOAT,
    period VARCHAR(50),
    start_date VARCHAR(20),
    next_payment VARCHAR(20)
);
