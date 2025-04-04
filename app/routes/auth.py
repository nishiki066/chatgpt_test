from flask import Blueprint, request, jsonify
from app.models.user import User
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
import logging
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

# 用户注册
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409

    # 创建用户实例，密码加密存储
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)

    # 保存到数据库
    try:
        db.session.add(new_user)
        db.session.commit()
        logging.info(f'User registered successfully: {username}')
        return jsonify({'message': 'User registered successfully', 'user_id': new_user.user_id}), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error registering user: {str(e)}')
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500


# 用户登录
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    # 验证用户是否存在
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'Invalid username or password'}), 401

    # 验证密码
    if not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid username or password'}), 401

    # 创建JWT令牌 (有效期7天)
    access_token = create_access_token(identity=user.user_id, expires_delta=timedelta(days=7))

    logging.info(f'User logged in successfully: {username}')

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user_id': user.user_id
    }), 200
