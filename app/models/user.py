from app import db

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    account_status = db.Column(db.Enum('active', 'banned', name='account_status_enum'), default='active')
    connection_status = db.Column(db.Enum('online', 'offline', name='connection_status_enum'), default='offline')
    role = db.Column(db.Enum('user', 'admin', name='role_enum'), default='user')
    balance = db.Column(db.Decimal(10, 2), default=0)
    last_login = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'
