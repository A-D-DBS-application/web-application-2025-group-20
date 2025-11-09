from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = db.Column(db.Text, nullable=False)
    role = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Debtor(db.Model):
    __tablename__ = 'debtor'

    national_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    address = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    financial_data_source = db.Column(db.Text)



