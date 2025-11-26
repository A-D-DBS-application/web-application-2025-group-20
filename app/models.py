from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    username = db.Column(db.String, primary_key=True)
    role = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Debtor(db.Model):
    __tablename__ = "debtors"

    national_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    financial_data_source = db.Column(db.String)
    user_username = db.Column(db.String, db.ForeignKey("users.username"))

class AuditLog(db.Model):
    __tablename__ = "audit_log"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, db.ForeignKey("users.username"), nullable=False)

    # What happened
    action = db.Column(db.String, nullable=False)  # e.g. "viewed", "exported", "updated"

    # What data was accessed
    resource_type = db.Column(db.String, nullable=False)  # e.g. "Debtor"
    resource_id = db.Column(db.String, nullable=False)     # e.g. national_id

    # When
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Optional details JSON/text
    details = db.Column(db.Text)
