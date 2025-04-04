import time
import logging
from jp_server.poller import poll_and_process_messages

logging.basicConfig(level=logging.INFO)

def main():
    logging.info(" 日本服务器启动：等待处理消息")

    while True:
        try:
            # 查询数据库中状态为 PENDING 的消息
            poll_and_process_messages()
        except Exception as e:
            logging.error(f" 主循环出错: {e}")

        time.sleep(2)  # 每 2 秒检查一次（可调节）

if __name__ == "__main__":
    main()
