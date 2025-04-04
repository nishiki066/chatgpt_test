# jp_server/poller.py
import time
import logging
from concurrent.futures import ThreadPoolExecutor

from jp_server.db import SessionLocal
from jp_server.constants import MessageStatus
from app.models.message import Message
from jp_server.openai_worker import handle_message

# 最大并发线程数，可按需调整
executor = ThreadPoolExecutor(max_workers=5)

def poll_and_process_messages():
    logging.info("[Poller] 启动消息轮询器...")
    while True:
        db = SessionLocal()
        try:
            # 查找 PENDING 状态的消息
            pending_messages = db.query(Message).filter(Message.status == MessageStatus.PENDING).all()
        except Exception as e:
            logging.error(f"[Poller] 查询消息失败: {e}")
            pending_messages = []
        finally:
            db.close()

        for msg in pending_messages:
            logging.info(f"[Poller] 分发消息处理任务: id={msg.id}, content={msg.content[:30]}...")
            # 提交到线程池，异步执行
            executor.submit(handle_message, msg.id)

        time.sleep(3)
