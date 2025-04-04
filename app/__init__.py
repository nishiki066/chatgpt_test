from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
# 初始化数据库
db = SQLAlchemy()

def create_app():
    # 创建 Flask 应用实例
    app = Flask(__name__)

    # 加载配置
    config_path = os.getenv("APP_CONFIG_MODULE", "config.Config")
    app.config.from_object(config_path)

    # 初始化数据库
    db.init_app(app)
    from app.models import user, message, session, usage
    from flask_jwt_extended import JWTManager
    jwt = JWTManager()
    jwt.init_app(app)



    # 启用跨域支持
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=app.config['CORS_SUPPORTS_CREDENTIALS'])

    # 注册蓝图（路由）
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.message import message_bp
    app.register_blueprint(message_bp, url_prefix='/message')

    from app.routes.session import session_bp
    app.register_blueprint(session_bp, url_prefix='/session')

    return app
