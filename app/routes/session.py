from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.session import Session
from app.models.message import Message
from app.models.usage import UsageRecord
import logging
from flask import request
# 创建 Blueprint
session_bp = Blueprint('session', __name__)
@session_bp.route('/<int:session_id>', methods=['DELETE'])
@jwt_required()
def delete_session(session_id):
    current_user_id = get_jwt_identity()

    # 查找会话
    session = Session.query.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404

    # 确保只能删除自己的会话
    if session.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized access'}), 403

    try:
        # 1. 找到会话中的所有消息
        messages = Message.query.filter_by(session_id=session_id).all()

        # 2. 先处理消息间的引用关系
        # 将所有引用到将被删除消息的 reply_to_message_id 设置为 NULL
        db.session.query(Message).filter(Message.reply_to_message_id.in_([m.id for m in messages])).update({Message.reply_to_message_id: None}, synchronize_session=False)

        # 3. 删除与这些消息相关的使用记录
        for message in messages:
            UsageRecord.query.filter_by(message_id=message.id).delete()

        # 4. 删除消息
        Message.query.filter_by(session_id=session_id).delete()

        # 5. 删除会话本身
        db.session.delete(session)
        db.session.commit()

        logging.info(f'Session deleted: id={session_id}, user_id={current_user_id}')
        return jsonify({'message': 'Session deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error deleting session: {str(e)}')
        return jsonify({'error': 'Failed to delete session', 'details': str(e)}), 500

@session_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_sessions(user_id):
    current_user_id = get_jwt_identity()

    # 确保只能获取自己的会话
    if user_id != current_user_id:
        return jsonify({'error': 'Unauthorized access'}), 403

    # 获取该用户的所有会话
    sessions = Session.query.filter_by(user_id=user_id).order_by(Session.created_at.desc()).all()

    return jsonify({
        'sessions': [
            {
                'id': session.id,
                'title': session.title,
                'created_at': session.created_at
            } for session in sessions
        ]
    }), 200


@session_bp.route('/create', methods=['POST'])
@jwt_required()
def create_session():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    title = data.get('title', '新会话')

    new_session = Session(
        user_id=current_user_id,
        title=title,
        status='active'
    )

    try:
        db.session.add(new_session)
        db.session.commit()

        return jsonify({
            'message': 'Session created successfully',
            'session_id': new_session.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to create session',
            'details': str(e)
        }), 500