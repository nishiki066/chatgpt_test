from flask import Blueprint, request, jsonify
from app.models.message import Message, MessageStatus
from app.models.user import User
from app.models.session import Session
from app import db
import logging
from flask_jwt_extended import jwt_required, get_jwt_identity

message_bp = Blueprint('message', __name__)


# 发送消息接口（带JWT权限认证）
@message_bp.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    data = request.get_json()

    # 获取用户认证信息（从 JWT 中提取，确保安全）
    current_user_id = get_jwt_identity()

    # 客户端发送过来的数据
    session_id = data.get('session_id')
    content = data.get('content')
    role = data.get('role', 'user')  # 默认角色为'user'

    # 必填字段检查
    if not session_id or not content:
        return jsonify({'error': 'Missing required parameters'}), 400

    # 校验session有效性
    session = Session.query.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404

    # 创建消息实例（状态pending）
    new_message = Message(
        user_id=current_user_id,
        session_id=session_id,
        role=role,
        content=content,
        status=MessageStatus.PENDING.value
    )

    # 保存消息到数据库，加入异常捕获
    try:
        db.session.add(new_message)
        db.session.commit()
        logging.info(f'New message created: id={new_message.id}, user_id={current_user_id}')
        return jsonify({
            'message': 'Message sent successfully',
            'message_id': new_message.id
        }), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error when sending message: {str(e)}')
        return jsonify({'error': 'Failed to send message', 'details': str(e)}), 500


# 获取会话中的所有消息
@message_bp.route('/<int:session_id>', methods=['GET'])
@jwt_required()
def get_messages(session_id):
    # 检查session是否存在
    session = Session.query.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404

    messages = Message.query.filter_by(session_id=session_id).order_by(Message.created_at.asc()).all()

    message_list = [{
        'id': msg.id,
        'user_id': msg.user_id,
        'role': msg.role,
        'content': msg.content,
        'status': msg.status,
        'created_at': msg.created_at
    } for msg in messages]

    return jsonify({'messages': message_list}), 200


# 实时获取最新消息（增量消息获取接口）
@message_bp.route('/<int:session_id>/updates', methods=['GET'])
@jwt_required()
def get_new_messages(session_id):
    last_message_id = request.args.get('last_message_id', 0, type=int)

    # 检查session存在性
    session = Session.query.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404

    # 获取比 last_message_id 新且状态为streaming或completed的消息
    messages = Message.query.filter(
        Message.session_id == session_id,
        Message.id > last_message_id,
        Message.status.in_([MessageStatus.STREAMING.value, MessageStatus.COMPLETED.value])
    ).order_by(Message.id.asc()).all()

    message_list = [{
        'id': m.id,
        'content': m.content,
        'status': m.status,
        'created_at': m.created_at
    } for m in messages]

    return jsonify({'messages': message_list}), 200
