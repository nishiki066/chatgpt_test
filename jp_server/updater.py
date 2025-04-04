# jp_server/updater.py
from db import SessionLocal
from app.models.message import Message
from app.models.usage import UsageRecord
from constants import MessageStatus
import logging


def update_message_streaming(message_id, content_piece):
    db = SessionLocal()
    try:
        message = db.query(Message).get(message_id)
        if message:
            message.content = (message.content or '') + content_piece
            db.commit()
    except Exception as e:
        logging.error(f"[Updater] 写入内容失败: {e}")
    finally:
        db.close()


def mark_completed(message_id):
    db = SessionLocal()
    try:
        message = db.query(Message).get(message_id)
        if message:
            message.status = MessageStatus.COMPLETED.value
            db.commit()
    except Exception as e:
        logging.error(f"[Updater] 标记 COMPLETED 失败: {e}")
    finally:
        db.close()


def mark_failed(message_id, error_msg=""):
    db = SessionLocal()
    try:
        message = db.query(Message).get(message_id)
        if message:
            message.status = MessageStatus.FAILED.value
            message.error_message = error_msg[:500]
            db.commit()
    except Exception as e:
        logging.error(f"[Updater] 标记 FAILED 失败: {e}")
    finally:
        db.close()


def record_usage(user_id, message_id, model, prompt_tokens, completion_tokens, cost):
    db = SessionLocal()
    try:
        usage = UsageRecord(
            user_id=user_id,
            message_id=message_id,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            cost=cost
        )
        db.add(usage)
        db.commit()
    except Exception as e:
        logging.error(f"[Updater] 记录 usage 失败: {e}")
    finally:
        db.close()

def mark_streaming(message_id):
    db = SessionLocal()
    try:
        message = db.query(Message).get(message_id)
        if message:
            message.status = MessageStatus.STREAMING.value
            db.commit()
    except Exception as e:
        logging.error(f"[Updater] 标记 STREAMING 失败: {e}")
    finally:
        db.close()
