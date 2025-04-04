# jp_server/constants.py
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# OpenAI API Key（从环境变量中获取）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
