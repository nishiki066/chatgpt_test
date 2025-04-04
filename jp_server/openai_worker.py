# jp_server/openai_worker.py
import openai
import logging

from jp_server.db import SessionLocal
from jp_server.constants import OPENAI_API_KEY, MessageStatus
from app.models.message import Message
from app.models.session import Session
from jp_server import updater

openai.api_key = OPENAI_API_KEY


def build_message_context(db, session_id):
    messages = db.query(Message).filter_by(session_id=session_id).order_by(Message.created_at.asc()).all()
    return [{'role': m.role, 'content': m.content} for m in messages]


def handle_message(message_id):
    db = SessionLocal()
    try:
        message = db.query(Message).get(message_id)
        if not message:
            logging.warning(f"[Worker] 找不到消息 ID: {message_id}")
            return

        if message.status != MessageStatus.PENDING:
            logging.info(f"[Worker] 消息 {message.id} 状态为 {message.status}，跳过")
            return

        session = db.query(Session).get(message.session_id)
        if not session:
            logging.warning(f"[Worker] 找不到会话 ID: {message.session_id}")
            return

        # 标记为 STREAMING
        updater.mark_streaming(message.id)

        context = build_message_context(db, message.session_id)
        model = message.model or "gpt-3.5-turbo"

        logging.info(f"[Worker] 调用 OpenAI 接口，模型={model}")

        response = openai.ChatCompletion.create(
            model=model,
            messages=context,
            stream=True
        )

        for chunk in response:
            delta = chunk['choices'][0]['delta']
            if 'content' in delta:
                updater.update_message_streaming(message.id, delta['content'])

        updater.mark_completed(message.id)
        logging.info(f"[Worker] 消息 {message.id} 处理完成")

    except Exception as e:
        logging.error(f"[Worker] OpenAI 处理失败: {e}")
        updater.mark_failed(message_id, str(e))

    finally:
        db.close()
