from app import db
from datetime import datetime

class Message(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    session_id = db.Column(db.BigInteger, db.ForeignKey('chat_sessions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    role = db.Column(db.Enum('user', 'assistant', 'system', name='role_enum'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('pending', 'processing', 'thinking', 'streaming', 'completed', 'error', name='status_enum'), default='pending')
    reply_to_message_id = db.Column(db.BigInteger, db.ForeignKey('chat_messages.id'), nullable=True)
    tokens_used = db.Column(db.Integer, nullable=True)
    error_message = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    session = db.relationship('Session', backref=db.backref('messages', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('messages', lazy='dynamic'))
    reply_to = db.relationship('Message', remote_side=[id], backref=db.backref('replies', lazy='dynamic'))

    def __repr__(self):
        return f'<Message {self.id}, Role {self.role}, Status {self.status}>'
