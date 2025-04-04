# jp_server/db.py
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from app import create_app

# 使用已有的 app 工厂方法来初始化数据库连接
app = create_app()
app.app_context().push()

db = SQLAlchemy(app)
