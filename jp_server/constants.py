#jp_server/constants.py
from enum import Enum
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class MessageStatus(str, Enum):
    PENDING = "pending"
    THINKING = "thinking"
    STREAMING = "streaming"
    COMPLETED = "completed"
    FAILED = "failed"
