import uuid
from datetime import datetime
from app import db

class Session(db.Model):
    __tablename__ = 'chat_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    # 自动生成唯一的 session_token
    session_token = db.Column(db.String(64), nullable=False, unique=True, default=lambda: uuid.uuid4().hex)

    title = db.Column(db.String(255), default='New Session')
    status = db.Column(db.String(20), default='active')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
