# app/utils/title_generator.py
import logging
import re
import requests
from typing import List, Dict, Any, Optional


class TitleGenerator:
    """
    会话标题生成器类
    提供两种生成标题的方法：
    1. 基于简单规则的标题生成
    2. 基于AI的高级标题生成（需要OpenAI API密钥）
    """

    @staticmethod
    def generate_basic_title(messages: List[Dict]) -> str:
        """
        基于简单规则生成标题

        从用户消息中提取关键内容，智能截取合适长度的标题文本

        参数:
            messages: 消息列表，每条消息包含 'role' 和 'content' 字段

        返回:
            str: 生成的标题
        """
        # 提取最多前3条用户消息
        user_messages = [m['content'] for m in messages if m['role'] == 'user'][:3]

        if not user_messages:
            return "新对话"  # 如果没有用户消息，返回默认标题

        # 使用第一条消息作为基础
        first_message = user_messages[0]

        # 简单清理文本：移除特殊字符，保留中文、英文字母、数字和空格
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', first_message)
        text = re.sub(r'\s+', ' ', text).strip()  # 合并多个空格

        # 智能截取标题
        if len(text) > 30:
            # 尝试在合适的位置截断，优先在空格处截断以保持词语的完整性
            cutoff = min(30, len(text))
            if ' ' in text[15:cutoff]:
                last_space = text[15:cutoff].rindex(' ') + 15
                title = text[:last_space]
            else:
                title = text[:cutoff]
            title += "..."  # 添加省略号表示标题被截断
        else:
            title = text

        # 标题太短时使用默认值
        if len(title) < 5:
            return "新对话"

        return title

    @staticmethod
    def generate_ai_title(messages: List[Dict], api_key: Optional[str] = None) -> str:
        """
        使用AI服务生成智能标题

        通过OpenAI API分析对话内容，生成更精确、更有语义的标题
        如果API调用失败，会回退到基本标题生成方法

        参数:
            messages: 消息列表，每条消息包含 'role' 和 'content' 字段
            api_key: OpenAI API密钥，如果为None则使用基本方法

        返回:
            str: 生成的标题
        """
        if not api_key:
            logging.warning("未提供AI服务API密钥，使用基本标题生成方法")
            return TitleGenerator.generate_basic_title(messages)

        try:
            # 准备对话数据
            # 只取前5条消息，避免请求过大
            conversation = messages[:5]

            # 如果对话为空，返回默认标题
            if not conversation:
                return "新对话"

            # 构建提示词
            prompt = "请根据以下对话为这个会话生成一个简短、具体且有描述性的标题（不超过15个字符）:\n\n"

            for msg in conversation:
                role = "用户" if msg['role'] == 'user' else "助手"
                prompt += f"{role}: {msg['content']}\n"

            # 调用OpenAI API
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "gpt-3.5-turbo",  # 使用较轻量的模型，减少延迟和成本
                "messages": [
                    {"role": "system",
                     "content": "你是一个精确的会话标题生成器。你的任务是为对话生成一个简短、具体且有描述性的标题，长度不超过15个字符。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 50,  # 限制输出长度
                "temperature": 0.7  # 适中的创造性
            }

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10  # 设置超时时间，避免请求卡住
            )

            if response.status_code == 200:
                # 成功获取响应
                result = response.json()
                title = result['choices'][0]['message']['content'].strip()

                # 清理标题：移除引号和多余的标点
                title = re.sub(r'^["\'"\']|["\'"\']$', '', title)
                title = re.sub(r'^标题[：:]\s*', '', title)  # 移除"标题："前缀

                # 确保标题不超过20个字符
                if len(title) > 20:
                    title = title[:18] + "..."

                return title
            else:
                # API调用失败，记录错误并回退到基本方法
                logging.error(f"调用AI服务失败: {response.status_code} - {response.text}")
                return TitleGenerator.generate_basic_title(messages)

        except Exception as e:
            # 捕获所有异常，确保即使AI生成失败也能返回一个标题
            logging.error(f"生成AI标题时出错: {str(e)}")
            return TitleGenerator.generate_basic_title(messages)