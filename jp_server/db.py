#jp_server/db.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from jp_config import Config

# 加载 Flask 应用
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ✅ 导入模型，确保所有外键引用表存在
from app.models import user, message, session, usage

# 初始化 session
with app.app_context():
    SessionLocal = scoped_session(sessionmaker(bind=db.engine))

# ✅ 可选调试
print(" 当前数据库连接:", Config.DB_HOST)
print(" 加载模型成功")
