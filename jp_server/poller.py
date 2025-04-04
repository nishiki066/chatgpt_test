# jp_server/poller.py
import time
import logging
from concurrent.futures import ThreadPoolExecutor

from db import SessionLocal
from constants import MessageStatus
from app.models.message import Message
from openai_worker import handle_message

# 最大并发线程数，可按需调整
executor = ThreadPoolExecutor(max_workers=5)

def poll_and_process_messages():
    logging.info("[Poller] 启动消息轮询器...")

    db = SessionLocal()
    try:
        pending_messages = db.query(Message).filter(Message.status == MessageStatus.PENDING).all()
    except Exception as e:
        logging.error(f"[Poller] 查询消息失败: {e}")
        pending_messages = []
    finally:
        db.close()

    for msg in pending_messages:
        logging.info(f"[Poller] 分发消息处理任务: id={msg.id}, content={msg.content[:30]}...")
        executor.submit(handle_message, msg.id)
