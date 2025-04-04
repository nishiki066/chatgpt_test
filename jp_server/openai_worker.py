#jp_server/openai_worker.py
import openai
from openai import OpenAI
import logging
import os
from jp_config import Config
import updater
from app.models.message import Message
from app.models.session import Session
from db import SessionLocal
from constants import MessageStatus
from dotenv import load_dotenv
# 加载环境变量
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# 创建 OpenAI 客户端实例
client = OpenAI(api_key=Config.OPENAI_API_KEY)

def build_message_context(db, session_id):
    messages = db.query(Message).filter_by(session_id=session_id).order_by(Message.created_at.asc()).all()
    return [{'role': m.role, 'content': m.content} for m in messages]

def handle_message(message_id):
    db = SessionLocal()
    try:
        message = db.query(Message).get(message_id)
        if not message or message.status != MessageStatus.PENDING:
            return

        # 查找 session
        session = db.query(Session).get(message.session_id)
        if not session:
            logging.warning(f"[Worker] 找不到会话 ID: {message.session_id}")
            return

        # 标记为 STREAMING
        message.status = MessageStatus.STREAMING.value
        db.commit()

        context = build_message_context(db, message.session_id)
        model = message.model or "gpt-3.5-turbo"
        logging.info(f"[Worker] 调用 OpenAI 接口，模型={model}")

        # 使用 stream 调用 OpenAI
        response = client.chat.completions.create(
            model=model,
            messages=context,
            stream=True
        )

        full_reply = ""
        for chunk in response:
            choice = chunk.choices[0]
            if choice.delta and choice.delta.content:
                content_piece = choice.delta.content
                full_reply += content_piece
                logging.info(f"[Stream] {content_piece}")

        # 新建一条 assistant 消息
        assistant_msg = Message(
            user_id=message.user_id,
            session_id=message.session_id,
            role="assistant",
            content=full_reply,
            status=MessageStatus.COMPLETED.value,
            model=model,
            reply_to_message_id=message.id
        )
        db.add(assistant_msg)

        # 原消息也标记为 COMPLETED（如果你愿意保留状态）
        message.status = MessageStatus.COMPLETED.value

        db.commit()
        logging.info(f"[Worker] 回复完成并保存，message_id={assistant_msg.id}")

    except Exception as e:
        logging.error(f"[Worker] OpenAI 处理失败: {e}")
        db.rollback()
        message.status = MessageStatus.FAILED.value
        message.error_message = str(e)[:500]
        db.commit()
    finally:
        db.close()

