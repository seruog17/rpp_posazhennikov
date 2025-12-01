from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(100))
    amount = db.Column(db.Float)
    period = db.Column(db.String(50))
    start_date = db.Column(db.String(20))
    next_payment = db.Column(db.String(20))

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(20))
    details = db.Column(db.String(200))
