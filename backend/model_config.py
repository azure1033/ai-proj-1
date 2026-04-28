"""
模型配置模块 - 支持多 Provider 切换（LLM 和 Embedding 独立配置）

LLM Provider:   zhipu | ollama | siliconflow
Embed Provider:  zhipu | local  | siliconflow

通过 .env 中的 LLM_PROVIDER 和 EMBEDDING_PROVIDER 变量控制
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# 从项目根目录加载 .env 文件
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# ===================== LLM Provider 配置 =====================

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "").strip().lower()

# 向后兼容：如果设置了 OLLAMA_MODEL 但未设置 LLM_PROVIDER，自动推断为 ollama
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "").strip()
if OLLAMA_MODEL and not LLM_PROVIDER:
    LLM_PROVIDER = "ollama"
    logger.info("检测到 OLLAMA_MODEL 已设置，自动推断 LLM_PROVIDER=ollama")

# 默认使用 zhipu
if not LLM_PROVIDER:
    LLM_PROVIDER = "zhipu"

# 各 Provider 的 API 配置
# base_url: API 基础地址，ChatOpenAI 会在其后追加 /chat/completions
PROVIDER_CONFIG = {
    "zhipu": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key_env": "ZHIPU_API_KEY",
        "model": "glm-4-flash",
    },
    "ollama": {
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        "api_key_env": None,
        "model": OLLAMA_MODEL or "qwen2.5:3b",
    },
    "siliconflow": {
        "base_url": "https://api.siliconflow.cn/v1",
        "api_key_env": "DEEPSEEK_API_KEY",
        "model": "deepseek-ai/DeepSeek-V2.5",
    },
}

if LLM_PROVIDER not in PROVIDER_CONFIG:
    logger.warning(f"未知的 LLM_PROVIDER: {LLM_PROVIDER}，回退到 zhipu")
    LLM_PROVIDER = "zhipu"

config = PROVIDER_CONFIG[LLM_PROVIDER]
BASE_URL = config["base_url"]
API_KEY = os.getenv(config["api_key_env"], "") if config["api_key_env"] else "dummy"
MODEL = config["model"]
IS_OLLAMA = LLM_PROVIDER == "ollama"

# API Key 缺失警告
if config["api_key_env"] and not os.getenv(config["api_key_env"], "").strip():
    logger.warning(
        f"LLM Provider '{LLM_PROVIDER}' 需要 {config['api_key_env']}，但未在 .env 中找到。"
        f"请设置 {config['api_key_env']}=your_key 或切换 LLM_PROVIDER"
    )


def get_openai_client():
    """获取 OpenAI 客户端 (main.py 使用)"""
    import openai
    return openai.OpenAI(api_key=API_KEY, base_url=BASE_URL)


def get_langchain_llm():
    """获取 LangChain LLM (weather_agent.py / agent.py 使用)
    
    根据 LLM_PROVIDER 返回对应的 ChatOpenAI 实例。
    """
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=MODEL,
        openai_api_key=API_KEY,
        openai_api_base=BASE_URL,  # base_url 已包含 /v1 或 /v4 路径前缀
        temperature=0.7,
    )


# ===================== Embedding Provider 配置 =====================

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "").strip().lower()

if not EMBEDDING_PROVIDER:
    EMBEDDING_PROVIDER = "zhipu"

ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "").strip()
ZHIPU_EMBEDDING_MODEL = os.getenv("ZHIPU_EMBEDDING_MODEL", "embedding-2").strip()


def get_embedding_function():
    """获取 Embedding 实例（根据 EMBEDDING_PROVIDER）
    
    Returns:
        Embeddings 实例，用于文档向量化和检索
    
    Provider:
        zhipu       → ZhipuAIEmbeddings (云端 API, 1024维)
        local       → HuggingFaceEmbeddings (本地 text2vec, 768维)
        siliconflow → OpenAIEmbeddings (云端 API)
    """
    if EMBEDDING_PROVIDER == "zhipu":
        if not ZHIPU_API_KEY:
            logger.warning("EMBEDDING_PROVIDER=zhipu 但 ZHIPU_API_KEY 未设置，回退到 local")
            return _get_local_embeddings()
        try:
            from langchain_community.embeddings import ZhipuAIEmbeddings
            logger.info(f"使用智谱 Embedding: model={ZHIPU_EMBEDDING_MODEL}")
            return ZhipuAIEmbeddings(
                model=ZHIPU_EMBEDDING_MODEL,
                api_key=ZHIPU_API_KEY,
            )
        except Exception as e:
            logger.warning(f"智谱 Embedding 初始化失败: {e}，回退到 local")
            return _get_local_embeddings()

    elif EMBEDDING_PROVIDER == "siliconflow":
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
