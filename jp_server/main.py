import time
import logging
from poller import poll_and_process_messages
import os
from dotenv import load_dotenv
from jp_config import Config
print(" Loaded DB:", Config.SQLALCHEMY_DATABASE_URI)
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
logging.basicConfig(level=logging.INFO)

def main():
    logging.info(" 日本服务器启动：等待处理消息")

    while True:
        try:
            poll_and_process_messages()
        except Exception as e:
            logging.error(f" 主循环出错: {e}")
        time.sleep(2)


if __name__ == "__main__":
    main()
