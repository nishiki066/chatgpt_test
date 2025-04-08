# 新增：删除会话
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
        # 1. 首先找到与此会话相关的所有消息
        from app.models.message import Message
        from app.models.usage import UsageRecord

        # 找到会话中的所有消息
        messages = Message.query.filter_by(session_id=session_id).all()

        # 2. 对每个消息，删除相关的使用记录
        for message in messages:
            # 找到与消息相关的使用记录
            usage_records = UsageRecord.query.filter_by(message_id=message.id).all()

            # 删除每个使用记录
            for record in usage_records:
                db.session.delete(record)

            # 删除消息
            db.session.delete(message)

        # 3. 最后删除会话本身
        db.session.delete(session)
        db.session.commit()

        logging.info(f'Session deleted: id={session_id}, user_id={current_user_id}')
        return jsonify({'message': 'Session deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error deleting session: {str(e)}')
        return jsonify({'error': 'Failed to delete session', 'details': str(e)}), 500