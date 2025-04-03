from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # 加密后的密码
    phone = db.Column(db.String(20), nullable=True)

    account_status = db.Column(db.String(20), default='active')  # active / suspended / etc.
    connection_status = db.Column(db.String(20), default='offline')  # online / offline
    role = db.Column(db.String(20), default='user')  # user / admin
    balance = db.Column(db.Float, default=0.0)

    last_login = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.username}>"
