"""
模型配置模块 - 纯配置读取器

通过 .env 中的 LLM_PROVIDER / EMBEDDING_PROVIDER 读取静态配置。
不再提供客户端工厂函数 — 客户端创建统一由 provider_manager 负责。

Public API:
    read_llm_config()      -> dict  {base_url, api_key, model, is_ollama}
    read_embedding_config() -> dict  {provider, api_key, model}
    get_embedding_function()       (保留，供 provider_manager 回退使用)
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# 从项目根目录加载 .env 文件
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# ===================== 内部变量（仅供公共函数使用） =====================

_LLM_PROVIDER = os.getenv("LLM_PROVIDER", "").strip().lower()

# 向后兼容：如果设置了 OLLAMA_MODEL 但未设置 LLM_PROVIDER，自动推断为 ollama
_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "").strip()
if _OLLAMA_MODEL and not _LLM_PROVIDER:
    _LLM_PROVIDER = "ollama"
    logger.info("检测到 OLLAMA_MODEL 已设置，自动推断 LLM_PROVIDER=ollama")

if not _LLM_PROVIDER:
    _LLM_PROVIDER = "zhipu"

_PROVIDER_CONFIG = {
    "zhipu": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key_env": "ZHIPU_API_KEY",
        "model": "glm-4-flash",
    },
    "ollama": {
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        "api_key_env": None,
        "model": _OLLAMA_MODEL or "qwen2.5:3b",
    },
    "siliconflow": {
        "base_url": "https://api.siliconflow.cn/v1",
        "api_key_env": "DEEPSEEK_API_KEY",
        "model": "deepseek-ai/DeepSeek-V2.5",
    },
}

if _LLM_PROVIDER not in _PROVIDER_CONFIG:
    logger.warning(f"未知的 LLM_PROVIDER: {_LLM_PROVIDER}，回退到 zhipu")
    _LLM_PROVIDER = "zhipu"

_config = _PROVIDER_CONFIG[_LLM_PROVIDER]
_BASE_URL = _config["base_url"]
_API_KEY = os.getenv(_config["api_key_env"], "") if _config["api_key_env"] else "dummy"
_MODEL = _config["model"]
_IS_OLLAMA = _LLM_PROVIDER == "ollama"

# API Key 缺失警告
if _config["api_key_env"] and not os.getenv(_config["api_key_env"], "").strip():
    logger.warning(
        f"LLM Provider '{_LLM_PROVIDER}' 需要 {_config['api_key_env']}，但未在 .env 中找到。"
        f"请设置 {_config['api_key_env']}=your_key 或切换 LLM_PROVIDER"
    )


# ===================== 公共 API =====================

def read_llm_config() -> dict:
    """读取 .env 中的 LLM 配置（纯数据，不创建客户端）
    
    Returns:
        {
            "base_url": str,   # API 基础地址（含 /v1 或 /v4 路径前缀）
            "api_key": str,    # API Key（Ollama 时为 "dummy"）
            "model": str,      # 模型名称
            "is_ollama": bool, # 是否 Ollama 本地模型
        }
    """
    return {
        "base_url": _BASE_URL,
        "api_key": _API_KEY,
        "model": _MODEL,
        "is_ollama": _IS_OLLAMA,
    }


def read_embedding_config() -> dict:
    """读取 .env 中的 Embedding 配置（纯数据，不创建客户端）
    
    Returns:
        {
            "provider": str,  # zhipu | local | siliconflow
            "api_key": str,   # API Key（local 时为空）
            "model": str,     # 模型名称
        }
    """
    provider = os.getenv("EMBEDDING_PROVIDER", "").strip().lower()
    if not provider:
        provider = "zhipu"

    api_key = ""
    model = ""

    if provider == "zhipu":
        api_key = os.getenv("ZHIPU_API_KEY", "").strip()
        model = os.getenv("ZHIPU_EMBEDDING_MODEL", "embedding-2").strip()
    elif provider == "siliconflow":
        api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        model = "BAAI/bge-large-zh-v1.5"
    # local: api_key and model stay empty

    return {
        "provider": provider,
        "api_key": api_key,
        "model": model,
    }


# ===================== Embedding 客户端工厂（保留，供 provider_manager 回退使用） =====================

def get_embedding_function():
    """获取 Embedding 实例（根据 EMBEDDING_PROVIDER）
    
    Returns:
        Embeddings 实例，用于文档向量化和检索
    
    Provider:
        zhipu       → ZhipuAIEmbeddings (云端 API, 1024维)
        local       → HuggingFaceEmbeddings (本地 text2vec, 768维)
        siliconflow → OpenAIEmbeddings (云端 API)
    """
    cfg = read_embedding_config()
    provider = cfg["provider"]

    if provider == "zhipu":
        if not cfg["api_key"]:
            logger.warning("EMBEDDING_PROVIDER=zhipu 但 ZHIPU_API_KEY 未设置，回退到 local")
            return _get_local_embeddings()
        try:
            from langchain_community.embeddings import ZhipuAIEmbeddings
            logger.info(f"使用智谱 Embedding: model={cfg['model']}")
            return ZhipuAIEmbeddings(
                model=cfg["model"],
                api_key=cfg["api_key"],
            )
        except Exception as e:
            logger.warning(f"智谱 Embedding 初始化失败: {e}，回退到 local")
            return _get_local_embeddings()

    elif provider == "siliconflow":
        try:
            from langchain_openai import OpenAIEmbeddings
            logger.info("使用 SiliconFlow Embedding")
            return OpenAIEmbeddings(
                model="BAAI/bge-large-zh-v1.5",
                openai_api_key=os.getenv("DEEPSEEK_API_KEY", ""),
                openai_api_base="https://api.siliconflow.cn/v1/",
                check_embedding_ctx_length=False,
            )
        except Exception as e:
            logger.warning(f"SiliconFlow Embedding 初始化失败: {e}，回退到 local")
            return _get_local_embeddings()

    else:  # "local" 或未知
        return _get_local_embeddings()


_embeddings = None  # 本地嵌入模型单例缓存


def _get_local_embeddings():
    """获取本地 HuggingFace Embeddings（懒加载单例）"""
    global _embeddings
    if _embeddings is None:
        logger.info("加载本地嵌入模型: shibing624/text2vec-base-chinese")
        from langchain_huggingface import HuggingFaceEmbeddings
        _embeddings = HuggingFaceEmbeddings(
            model_name="shibing624/text2vec-base-chinese",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings
