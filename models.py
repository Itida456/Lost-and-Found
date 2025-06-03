from app import db
from datetime import datetime

class ReportedItem(db.Model):
    __tablename__ = 'reported_items'
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(255), nullable=False)
    item_desc = db.Column(db.Text, nullable=False)
    date_lost = db.Column(db.Date, nullable=False)
    location_lost = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(100), nullable=False)
    date_reported = db.Column(db.DateTime, default=datetime.utcnow)

class ClaimedItem(db.Model):
    __tablename__ = 'claimed_items'
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(255), nullable=False)
    item_desc = db.Column(db.Text, nullable=False)
    date_claimed = db.Column(db.Date, nullable=False)
    location_lost = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending')
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    reg_number = db.Column(db.String(9), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)