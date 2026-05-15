"""
MySQL 异步数据库引擎与会话管理

提供:
- create_async_engine 引擎工厂
- AsyncSession 工厂 (async_sessionmaker)
- FastAPI Depends 注入: get_db()
- 建表: init_db()
- MySQL 降级开关: is_mysql_enabled()
"""
import os
import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://ai_chat_user:chat123@localhost:3306/ai_chat")

_engine = None
_async_session_factory = None


def is_mysql_enabled() -> bool:
    """检测是否启用 MySQL 模式"""
    return os.getenv("USE_MYSQL", "").lower() == "true"


def _get_engine():
    """懒加载异步引擎"""
    global _engine
    if _engine is None and is_mysql_enabled():
        _engine = create_async_engine(
            DATABASE_URL,
            echo=False,
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,
        )
    return _engine


def _get_session_factory():
    """懒加载异步 session 工厂"""
    global _async_session_factory
    engine = _get_engine()
    if _async_session_factory is None and engine is not None:
        _async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession | None, None]:
    """FastAPI 依赖注入: 提供异步数据库会话"""
    if not is_mysql_enabled():
        yield None
        return

    session_factory = _get_session_factory()
    if session_factory is None:
        yield None
        return

    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """初始化数据库表结构（create_all）+ 预设 provider 数据"""
    if not is_mysql_enabled():
        logger.info("USE_MYSQL=false, 跳过数据库初始化（使用内存 dict 模式）")
        return

    engine = _get_engine()
    if engine is None:
        logger.warning("数据库引擎未就绪，跳过表初始化")
        return

    # 延迟导入 models 避免循环依赖
    from models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("数据库表初始化完成")

    # 初始化预设 provider
    await _init_preset_providers(engine)


async def _init_preset_providers(engine) -> None:
    """初始化预设模型提供商（INSERT OR IGNORE）"""
    from sqlalchemy import text
    from encryption import encrypt

    empty_key = encrypt("")

    # (id, name, type, base_url, model_name, is_local)
    preset_defs = [
        # LLM presets
        ("zhipu",        "智谱 AI",        "llm", "https://open.bigmodel.cn/api/paas/v4",  "glm-4-flash",                     False),
        ("deepseek",     "DeepSeek",        "llm", "https://api.deepseek.com/v1",            "deepseek-chat",                    False),
        ("siliconflow",  "SiliconFlow",     "llm", "https://api.siliconflow.cn/v1",          "deepseek-ai/DeepSeek-V2.5",         False),
        ("openai",       "OpenAI",          "llm", "https://api.openai.com/v1",              "gpt-4o-mini",                      False),
        ("groq",         "Groq",            "llm", "https://api.groq.com/openai/v1",         "llama-3.3-70b-versatile",           False),
        ("ollama",       "Ollama 本地",     "llm", "http://localhost:11434/v1",              "qwen2.5:3b",                       False),
        # Embedding presets
        ("zhipu-emb",       "智谱 Embedding",       "embedding", "https://open.bigmodel.cn/api/paas/v4",  "embedding-2",                       False),
        ("openai-emb",      "OpenAI Embedding",     "embedding", "https://api.openai.com/v1",              "text-embedding-3-small",            False),
        ("siliconflow-emb", "SiliconFlow Embedding","embedding", "https://api.siliconflow.cn/v1",          "BAAI/bge-large-zh-v1.5",            False),
        ("local-emb",       "本地 text2vec",        "embedding", "",                                        "shibing624/text2vec-base-chinese",  True),
    ]

    async with engine.begin() as conn:
        for idx, (pid, pname, ptype, purl, pmodel, plocal) in enumerate(preset_defs):
            # 第一个 LLM 和 第一个 Embedding 默认激活
            first_llm = idx == 0
            first_emb = ptype == "embedding" and (
                idx == next(i for i, d in enumerate(preset_defs) if d[2] == "embedding")
            )
            is_active = first_llm or first_emb

            await conn.execute(text(
                "INSERT IGNORE INTO model_providers "
                "(id, name, provider_type, base_url, api_key, model_name, is_active, is_preset, is_local, created_at, updated_at) "
                "VALUES (:id, :name, :type, :url, :key, :model, :active, 1, :local, NOW(), NOW())"
            ), {
                "id": pid, "name": pname, "type": ptype, "url": purl,
                "key": empty_key, "model": pmodel,
                "active": is_active, "local": plocal,
            })

    logger.info(f"已初始化 {len(preset_defs)} 个预设 provider")
