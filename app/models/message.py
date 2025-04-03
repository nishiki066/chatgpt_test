from app import db
from datetime import datetime
from enum import Enum

# ✅ 消息状态枚举
class MessageStatus(Enum):
    PENDING = "pending"
    THINKING = "thinking"
    STREAMING = "streaming"
    COMPLETED = "completed"
    ERROR = "error"

# ✅ 消息模型
class Message(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    role = db.Column(db.String(20), default='user')  # user / assistant / system
    model = db.Column(db.String(50), nullable=True)
    content = db.Column(db.Text, nullable=False)

    status = db.Column(db.String(20), default=MessageStatus.PENDING.value)
    reply_to_message_id = db.Column(db.Integer, nullable=True)
    tokens_used = db.Column(db.Integer, nullable=True)
    error_message = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Message {self.id} (session: {self.session_id})>"
