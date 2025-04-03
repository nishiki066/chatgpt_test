from flask import Blueprint, request, jsonify
from app.models.session import Session
from app.models.user import User
from app import db
import logging
from flask_jwt_extended import jwt_required, get_jwt_identity

session_bp = Blueprint('session', __name__)

# 创建新会话（JWT保护）
@session_bp.route('/create', methods=['POST'])
@jwt_required()
def create_session():
    data = request.get_json()

    current_user_id = get_jwt_identity()

    title = data.get('title', 'New Session')

    # 创建会话实例
    new_session = Session(user_id=current_user_id, title=title)

    # 保存到数据库（异常捕获）
    try:
        db.session.add(new_session)
        db.session.commit()
        logging.info(f'New session created: id={new_session.id}, user_id={current_user_id}')
        return jsonify({
            'message': 'Session created successfully',
            'session_id': new_session.id
        }), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error creating session: {str(e)}')
        return jsonify({'error': 'Failed to create session', 'details': str(e)}), 500


# 获取用户的所有会话
@session_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_sessions(user_id):
    current_user_id = get_jwt_identity()

    # 安全校验，确保用户只能访问自己的会话
    if current_user_id != user_id:
        return jsonify({'error': 'Unauthorized access'}), 403

    sessions = Session.query.filter_by(user_id=user_id).order_by(Session.created_at.desc()).all()

    session_list = [{
        'id': s.id,
        'user_id': s.user_id,
        'title': s.title,
        'created_at': s.created_at
    } for s in sessions]

    return jsonify({'sessions': session_list}), 200
