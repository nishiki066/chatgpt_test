# jp_server/jp_config.py
import os
from dotenv import load_dotenv

# 加载 jp_server 目录下的 .env 文件
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

print(" 当前数据库连接:", os.getenv("DB_HOST"))
class Config:
    # OpenAI 配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # 数据库配置
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4"
    )
