from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.session import Session
from app.models.message import Message
from app.models.usage import UsageRecord
import logging
import os
from app.utils.title_generator import TitleGenerator  # 导入标题生成器

# 创建 Blueprint
session_bp = Blueprint('session', __name__)


# 会话详情获取接口
@session_bp.route('/detail/<int:session_id>', methods=['GET'])
@jwt_required()
def get_session(session_id):
    current_user_id = get_jwt_identity()

    # 查找会话
    session = Session.query.get(session_id)
    if not session:
        return jsonify({'error': '会话不存在'}), 404

    # 确保只能查看自己的会话
    if session.user_id != current_user_id:
        return jsonify({'error': '无权查看此会话'}), 403

    return jsonify({
        'id': session.id,
        'title': session.title,
        'status': session.status,
        'created_at': session.created_at,
        'updated_at': session.updated_at
    }), 200


# 会话删除接口
@session_bp.route('/<int:session_id>', methods=['DELETE'])
@jwt_required()
def delete_session(session_id):
    current_user_id = get_jwt_identity()

    # 查找会话
    session = Session.query.get(session_id)
    if not session:
        return jsonify({'error': '会话不存在'}), 404

    # 确保只能删除自己的会话
    if session.user_id != current_user_id:
        return jsonify({'error': '无权操作此会话'}), 403

    try:
        # 1. 找到会话中的所有消息
        messages = Message.query.filter_by(session_id=session_id).all()

        # 2. 先处理消息间的引用关系
        # 将所有引用到将被删除消息的 reply_to_message_id 设置为 NULL
        db.session.query(Message).filter(Message.reply_to_message_id.in_([m.id for m in messages])).update(
            {Message.reply_to_message_id: None}, synchronize_session=False)

        # 3. 删除与这些消息相关的使用记录
        for message in messages:
            UsageRecord.query.filter_by(message_id=message.id).delete()

        # 4. 删除消息
        Message.query.filter_by(session_id=session_id).delete()

        # 5. 删除会话本身
        db.session.delete(session)
        db.session.commit()

        logging.info(f'会话已删除: id={session_id}, user_id={current_user_id}')
        return jsonify({'message': '会话删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f'删除会话失败: {str(e)}')
        return jsonify({'error': '删除会话失败', 'details': str(e)}), 500


# 获取用户的所有会话
@session_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_sessions(user_id):
    current_user_id = get_jwt_identity()

    # 确保只能获取自己的会话
    if user_id != current_user_id:
        return jsonify({'error': '无权访问此数据'}), 403

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


# 创建新会话接口
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
            'message': '会话创建成功',
            'session_id': new_session.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': '创建会话失败',
            'details': str(e)
        }), 500


# 更新会话接口（用于重命名会话）
@session_bp.route('/<int:session_id>', methods=['PATCH'])
@jwt_required()
def update_session(session_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    title = data.get('title')

    if not title:
        return jsonify({'error': '标题不能为空'}), 400

    # 查找会话
    session = Session.query.get(session_id)
    if not session:
        return jsonify({'error': '会话不存在'}), 404

    # 确保只能修改自己的会话
    if session.user_id != current_user_id:
        return jsonify({'error': '无权修改此会话'}), 403

    try:
        session.title = title
        db.session.commit()

        logging.info(f'会话标题已更新: id={session_id}, 新标题="{title}"')
        return jsonify({
            'message': '会话更新成功',
            'session_id': session.id,
            'title': session.title
        }), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f'更新会话失败: {str(e)}')
        return jsonify({'error': '更新会话失败', 'details': str(e)}), 500


# 智能生成会话标题接口
@session_bp.route('/<int:session_id>/generate-title', methods=['POST'])
@jwt_required()
def generate_session_title(session_id):
    current_user_id = get_jwt_identity()

    # 查找会话
    session = Session.query.get(session_id)
    if not session:
        return jsonify({'error': '会话不存在'}), 404

    # 确保只能操作自己的会话
    if session.user_id != current_user_id:
        return jsonify({'error': '无权操作此会话'}), 403

    try:
        # 获取会话中的所有消息
        messages = Message.query.filter_by(session_id=session_id).order_by(Message.created_at.asc()).all()

        if not messages:
            return jsonify({'error': '会话中没有消息'}), 400

        # 将消息转换为字典格式，便于标题生成器处理
        message_dicts = []
        for msg in messages:
            message_dicts.append({
                'role': msg.role,
                'content': msg.content
            })

        # 获取OpenAI API密钥(如果配置了的话)
        api_key = os.getenv("OPENAI_API_KEY")

        # 生成标题(根据是否有API密钥使用不同的方法)
        if api_key:
            title = TitleGenerator.generate_ai_title(message_dicts, api_key)
            logging.info(f"使用AI生成标题: {title}")
        else:
            title = TitleGenerator.generate_basic_title(message_dicts)
            logging.info(f"使用基本方法生成标题: {title}")

        # 更新会话标题
        session.title = title
        db.session.commit()

        return jsonify({
            'message': '标题生成成功',
            'session_id': session.id,
            'title': session.title
        }), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f'生成标题失败: {str(e)}')
        return jsonify({'error': '生成标题失败', 'details': str(e)}), 500