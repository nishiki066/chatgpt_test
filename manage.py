from app import create_app, db
from app.models.user import User
from app.models.session import Session
from app.models.message import Message
from app.models.usage import UsageRecord

app = create_app()

# 👇 添加 shell 上下文处理器
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Session': Session,
        'Message': Message,
        'UsageRecord': UsageRecord
    }
