"""
SQLAlchemy ORM 模型

表:
- sessions: 会话元数据
- messages: 聊天消息（外键关联 sessions，CASCADE 删除）
"""
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Enum, JSON, DateTime, ForeignKey, BigInteger, Index, Boolean
from sqlalchemy.orm import DeclarativeBase, relationship
import enum


class Base(DeclarativeBase):
    pass


class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, comment="UUID")
    name = Column(String(100), nullable=False, default="新会话")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # 关系
    messages = relationship("MessageModel", back_populates="session", cascade="all, delete-orphan", lazy="selectin")

    __table_args__ = (
        Index("idx_sessions_updated", updated_at.desc()),
    )

    def __repr__(self) -> str:
        return f"<Session {self.id}: {self.name}>"


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    intent = Column(String(50), nullable=True)
    steps = Column(JSON, nullable=True, comment="Agent 推理步骤 [{tool, input, output}]")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # 关系
    session = relationship("SessionModel", back_populates="messages")

    __table_args__ = (
        Index("idx_messages_session_time", "session_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Message {self.id} [{self.role.value}] in {self.session_id}>"


class ProviderType(str, enum.Enum):
    llm = "llm"
    embedding = "embedding"


class ModelProvider(Base):
    __tablename__ = "model_providers"

    id = Column(String(50), primary_key=True, comment="唯一标识")
    name = Column(String(100), nullable=False, comment="显示名称")
    provider_type = Column(Enum(ProviderType), nullable=False, comment="llm 或 embedding")
    base_url = Column(String(500), nullable=False, comment="API 基础地址")
    api_key = Column(String(2000), nullable=False, default="", comment="Fernet 加密后的 API Key")
    model_name = Column(String(100), nullable=False, comment="默认模型名")
    is_active = Column(Boolean, nullable=False, default=False, comment="当前活跃")
    is_preset = Column(Boolean, nullable=False, default=False, comment="预设不可删")
    is_local = Column(Boolean, nullable=False, default=False, comment="本地模型（不调用 API）")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<ModelProvider {self.id} [{self.provider_type.value}]: {self.name}>"
