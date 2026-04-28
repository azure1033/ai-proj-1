"""
会话记忆模块 - 管理对话历史和上下文

提供:
- 会话级别的消息存储
- 上下文窗口管理（防止 token 溢出）
- 用户偏好存储（可选）
"""

from typing import TypedDict
from uuid import uuid4

# 配置常量
MAX_MESSAGES = 10  # 最近 10 轮对话
MAX_TOKENS = 4000  # 约 16000 字符

# 消息结构
class Message(TypedDict):
    role: str  # "user" or "assistant"
    content: str
    intent: str | None  # 意图标签，可选


# 全局会话存储: Dict[session_id, List[Message]]
sessions: dict[str, list[Message]] = {}

# 全局偏好存储: Dict[session_id, Dict[key, value]]
preferences: dict[str, dict[str, str]] = {}


def get_or_create_session(session_id: str | None = None) -> str:
    """获取或创建会话 ID"""
    if session_id and session_id in sessions:
        return session_id
    new_id = session_id or str(uuid4())
    sessions[new_id] = []
    preferences[new_id] = {}
    
    # 如果有 session_manager，同步创建元数据
    try:
        from session_manager import create_session
        create_session(new_id)
    except ImportError:
        pass
    
    return new_id


def add_message(session_id: str, role: str, content: str, intent: str | None = None) -> None:
    """添加消息到会话"""
    if session_id not in sessions:
        sessions[session_id] = []
        preferences[session_id] = {}
    msg: Message = {"role": role, "content": content}
    if intent:
        msg["intent"] = intent
    sessions[session_id].append(msg)
    
    # 如果有 session_manager，同步更新元数据
    try:
        from session_manager import touch_session
        touch_session(session_id)
    except ImportError:
        pass


def get_history(session_id: str) -> list[Message]:
    """获取会话历史"""
    return sessions.get(session_id, [])


def clear_history(session_id: str) -> None:
    """清除会话历史"""
    if session_id in sessions:
        sessions[session_id] = []


def get_context_window(session_id: str, current_query: str = "") -> list[Message]:
    """
    获取上下文窗口 - 限制消息数量和 token 数
    
    策略:
    1. 先按 MAX_MESSAGES 限制消息数
    2. 再按 MAX_TOKENS 限制 token 数
    """
    history = sessions.get(session_id, [])
    
    if not history:
        return []
    
    # 1. 滚动窗口 - 保留最近 N 条
    windowed = history[-MAX_MESSAGES:] if len(history) > MAX_MESSAGES else history
    
    # 2. Token 预算控制 - 渐进截断最旧消息
    # 简单估算：中文约 2 字符/token，英文约 4 字符/token
    # 取保守值 2
    def estimate_tokens(messages: list[Message]) -> int:
        total = 0
        for msg in messages:
            # role + ": " + content
            total += len(msg["content"]) // 2 + 10
        return total
    
    # 渐进截断直到符合预算
    while estimate_tokens(windowed) > MAX_TOKENS and len(windowed) > 1:
        windowed = windowed[1:]
    
    return windowed


def set_preference(session_id: str, key: str, value: str) -> None:
    """设置用户偏好"""
    if session_id not in preferences:
        preferences[session_id] = {}
    preferences[session_id][key] = value


def get_preference(session_id: str, key: str) -> str | None:
    """获取用户偏好"""
    return preferences.get(session_id, {}).get(key)


def get_all_preferences(session_id: str) -> dict[str, str]:
    """获取所有用户偏好"""
    return preferences.get(session_id, {}).copy()


def delete_preferences(session_id: str) -> None:
    """删除所有用户偏好"""
    if session_id in preferences:
        del preferences[session_id]