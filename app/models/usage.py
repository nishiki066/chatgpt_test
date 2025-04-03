from app import db
from datetime import datetime

class UsageRecord(db.Model):
    __tablename__ = 'usage_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('chat_messages.id'), nullable=False)

    model = db.Column(db.String(50), nullable=False)              # 使用的模型，比如 gpt-3.5-turbo
    prompt_tokens = db.Column(db.Integer, nullable=False, default=0)
    completion_tokens = db.Column(db.Integer, nullable=False, default=0)
    total_tokens = db.Column(db.Integer, nullable=False, default=0)

    cost = db.Column(db.Float, nullable=False, default=0.0)       # 本次消耗的金额（美元）
    currency = db.Column(db.String(10), default="USD")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<UsageRecord message_id={self.message_id} tokens={self.total_tokens} cost={self.cost}>"
