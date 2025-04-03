from flask import Blueprint, request, jsonify
from app.models.session import Session
from app.models.user import User
from app import db
import logging
from flask_jwt_extended import jwt_required, get_jwt_identity

session_bp = Blueprint('session', __name__)

# ✅ 创建新会话（JWT保护）
@session_bp.route('/create', methods=['POST'])
@jwt_required()
def create_session():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    title = data.get('title', 'New Session')

    new_session = Session(user_id=current_user_id, title=title)

    try:
        db.session.add(new_session)
        db.session.commit()
        logging.info(f'New session created: id={new_session.id}, user_id={current_user_id}')
        return jsonify({
            'message': 'Session created successfully',
            'session_id': new_session.id,
            'session_token': new_session.session_token  # ✅ 返回 token
        }), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error creating session: {str(e)}')
        return jsonify({'error': 'Failed to create session', 'details': str(e)}), 500


# ✅ 获取用户的所有会话
@session_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_sessions(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({'error': 'Unauthorized access'}), 403

    sessions = Session.query.filter_by(user_id=user_id).order_by(Session.created_at.desc()).all()

    session_list = [{
        'id': s.id,
        'user_id': s.user_id,
        'session_token': s.session_token,
        'title': s.title,
        'status': s.status,
        'created_at': s.created_at,
        'updated_at': s.updated_at
    } for s in sessions]

    return jsonify({'sessions': session_list}), 200


# ✅ 新增：通过 session_token 获取单个会话（推荐用于日本服务器或跨端通信）
@session_bp.route('/token/<string:session_token>', methods=['GET'])
@jwt_required()
def get_session_by_token(session_token):
    session = Session.query.filter_by(session_token=session_token).first()

    if not session:
        return jsonify({'error': 'Session not found'}), 404

    current_user_id = get_jwt_identity()
    if session.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized access'}), 403

    return jsonify({
        'id': session.id,
        'user_id': session.user_id,
        'session_token': session.session_token,
        'title': session.title,
        'status': session.status,
        'created_at': session.created_at,
        'updated_at': session.updated_at
    }), 200
