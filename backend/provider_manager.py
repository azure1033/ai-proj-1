"""
模型提供商管理器

管理 LLM 和 Embedding 提供商的动态配置与客户端创建。
配置从 MySQL 读取，支持运行时切换无需重启。

用法:
    from provider_manager import get_provider_manager
    mgr = get_provider_manager()
    client = mgr.get_active_llm_client()       # openai.OpenAI
    llm = mgr.get_active_llm_config()          # ChatOpenAI (LangChain)
    embeddings = mgr.get_active_embedding()     # Embeddings (LangChain)
"""
import logging
from typing import Optional

import openai

from encryption import decrypt

logger = logging.getLogger(__name__)

# 缓存配置（内存中，避免每次调用的同步问题）
_cache: dict = {
    "llm_client": None,       # openai.OpenAI
    "llm_config": None,       # ChatOpenAI
    "embedding_client": None, # Embeddings
    "llm_id": None,
    "embedding_id": None,
}


class ModelProviderManager:
    """单例管理器，提供 LLM 和 Embedding 客户端"""

    def get_active_llm_client(self) -> Optional[openai.OpenAI]:
        """获取当前活跃的 LLM OpenAI 客户端（用于非 LangChain 调用）"""
        if _cache["llm_client"] is None:
            self._reload_llm_sync()
        return _cache["llm_client"]

    def get_active_llm_config(self):
        """获取当前活跃的 LLM LangChain ChatOpenAI 实例"""
        if _cache["llm_config"] is None:
            self._reload_llm_sync()
        return _cache["llm_config"]

    def get_active_embedding(self):
        """获取当前活跃的 Embedding 实例"""
        if _cache["embedding_client"] is None:
            self._reload_embedding_sync()
        return _cache["embedding_client"]

    def get_active_embedding_id(self) -> str:
        """获取当前活跃 Embedding provider 的 ID"""
        return _cache.get("embedding_id", "") or ""

    def _reload_llm_sync(self):
        """同步加载 LLM 配置到缓存（从 model_config 兼容层读取）"""
        from model_config import get_openai_client, get_langchain_llm, MODEL
        try:
            _cache["llm_client"] = get_openai_client()
            _cache["llm_config"] = get_langchain_llm()
        except Exception as e:
            logger.warning(f"LLM 客户端创建失败: {e}")

    def _reload_embedding_sync(self):
        """同步加载 Embedding 配置到缓存"""
        from model_config import get_embedding_function
        try:
            _cache["embedding_client"] = get_embedding_function()
        except Exception as e:
            logger.warning(f"Embedding 客户端创建失败: {e}")

    async def reload_from_db(self, db) -> None:
        """从数据库重新加载所有配置并刷新缓存"""
        await self._reload_llm(db)
        await self._reload_embedding(db)

    async def _reload_llm(self, db) -> None:
        """从 DB 加载活跃 LLM provider 并创建客户端"""
        from sqlalchemy import select
        from models import ModelProvider, ProviderType

        result = await db.execute(
            select(ModelProvider)
            .where(ModelProvider.provider_type == ProviderType.llm, ModelProvider.is_active == True)
            .limit(1)
        )
        provider = result.scalar_one_or_none()
        if not provider:
            logger.warning("没有活跃的 LLM provider")
            return

        api_key = decrypt(provider.api_key) or ""
        _cache["llm_id"] = provider.id

        # 非本地模型无 API Key 时跳过客户端创建，保留旧缓存
        if not api_key.strip() and not provider.is_local:
            logger.warning(f"LLM provider '{provider.name}' 未设置 API Key，跳过客户端创建。请先在设置中填入 API Key 再激活。")
            return

        # openai.OpenAI client
        try:
            _cache["llm_client"] = openai.OpenAI(
                api_key=api_key,
                base_url=provider.base_url,
            )
        except Exception as e:
            logger.warning(f"OpenAI 客户端创建失败: {e}")

        # LangChain ChatOpenAI
        try:
            from langchain_openai import ChatOpenAI
            _cache["llm_config"] = ChatOpenAI(
                model=provider.model_name,
                openai_api_key=api_key,
                openai_api_base=provider.base_url,
                temperature=0.7,
            )
            logger.info(f"LLM provider 已激活: {provider.name} ({provider.model_name})")
        except Exception as e:
            logger.warning(f"ChatOpenAI 创建失败: {e}")

    async def _reload_embedding(self, db) -> None:
        """从 DB 加载活跃 Embedding provider 并创建客户端"""
        from sqlalchemy import select
        from models import ModelProvider, ProviderType

        result = await db.execute(
            select(ModelProvider)
            .where(ModelProvider.provider_type == ProviderType.embedding, ModelProvider.is_active == True)
            .limit(1)
        )
        provider = result.scalar_one_or_none()
        if not provider:
            logger.warning("没有活跃的 Embedding provider")
            return

        _cache["embedding_id"] = provider.id

        if provider.is_local:
            # 本地模型
            _cache["embedding_client"] = _create_local_embedding()
            logger.info(f"Embedding provider 已激活: {provider.name} (本地)")
            return

        api_key = decrypt(provider.api_key) or ""
        if not api_key.strip():
            logger.warning(f"Embedding provider '{provider.name}' 未设置 API Key，回退到本地模型")
            _cache["embedding_client"] = _create_local_embedding()
            return
        try:
            from langchain_openai import OpenAIEmbeddings
            _cache["embedding_client"] = OpenAIEmbeddings(
                model=provider.model_name,
                openai_api_key=api_key,
                openai_api_base=provider.base_url,
                check_embedding_ctx_length=False,
            )
            logger.info(f"Embedding provider 已激活: {provider.name} ({provider.model_name})")
        except Exception as e:
            logger.warning(f"Embedding 客户端创建失败: {e}，尝试回退到本地模型")
            local = _create_local_embedding()
            if local is not None:
                _cache["embedding_client"] = local
            else:
                logger.warning("本地嵌入模型也不可用，Embedding 功能暂不可用")

    async def switch_provider(self, provider_id: str, db) -> bool:
        """切换活跃 provider（同一 type 内取消其他激活）"""
        from sqlalchemy import select, update
        from models import ModelProvider, ProviderType

        target = await db.get(ModelProvider, provider_id)
        if not target:
            return False

        # 同 type 全部取消激活
        await db.execute(
            update(ModelProvider)
            .where(ModelProvider.provider_type == target.provider_type)
            .values(is_active=False)
        )

        # 激活目标
        target.is_active = True
        await db.flush()

        # 刷新缓存
        if target.provider_type == ProviderType.llm:
            await self._reload_llm(db)
        else:
            await self._reload_embedding(db)

        return True

    async def test_connection(self, provider_id: str, db, api_key_override: str | None = None) -> dict:
        """测试 provider 连接（调用 /models 端点验证）"""
        from sqlalchemy import select
        from models import ModelProvider
        import httpx

        result = await db.execute(select(ModelProvider).where(ModelProvider.id == provider_id))
        provider = result.scalar_one_or_none()
        if not provider:
            return {"success": False, "error": "Provider 不存在"}

        if api_key_override is not None:
            api_key = api_key_override
        else:
            api_key = decrypt(provider.api_key) or ""
        base_url = provider.base_url.rstrip("/")

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                headers = {"Authorization": f"Bearer {api_key}"}
                resp = await client.get(f"{base_url}/models", headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    model_count = len(data.get("data", []))
                    return {"success": True, "model_count": model_count}
                else:
                    return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
        except httpx.TimeoutException:
            return {"success": False, "error": "连接超时（5s）"}
        except Exception as e:
            return {"success": False, "error": str(e)}


_provider_manager: Optional[ModelProviderManager] = None


def get_provider_manager() -> ModelProviderManager:
    """获取单例 ModelProviderManager"""
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = ModelProviderManager()
    return _provider_manager


# 本地 embedding 单例
_local_embeddings = None


def _create_local_embedding():
    """创建本地 HuggingFace Embeddings（可能因依赖缺失返回 None）"""
    global _local_embeddings
    if _local_embeddings is None:
        try:
            logger.info("加载本地嵌入模型: shibing624/text2vec-base-chinese")
            from langchain_huggingface import HuggingFaceEmbeddings
            _local_embeddings = HuggingFaceEmbeddings(
                model_name="shibing624/text2vec-base-chinese",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
        except ModuleNotFoundError:
            logger.warning("langchain_huggingface 未安装，本地嵌入模型不可用")
            return None
        except Exception as e:
            logger.warning(f"本地嵌入模型加载失败: {e}")
            return None
    return _local_embeddings
