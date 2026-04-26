"""
模型配置模块 - 支持本地 Ollama 和远程 API 切换
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 从项目根目录加载 .env 文件
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# 检测是否使用 Ollama
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "").strip()

if OLLAMA_MODEL:
    # 使用本地 Ollama
    BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    API_KEY = "dummy"  # Ollama 不需要 API Key
    MODEL = OLLAMA_MODEL
    IS_OLLAMA = True
else:
    # 使用远程 API
    BASE_URL = "https://api.siliconflow.cn/"
    API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    MODEL = "deepseek-ai/DeepSeek-V2.5"
    IS_OLLAMA = False


def get_openai_client():
    """获取 OpenAI 客户端 (main.py 使用)"""
    import openai
    return openai.OpenAI(api_key=API_KEY, base_url=BASE_URL + "/v1")


def get_langchain_llm():
    """获取 LangChain LLM (weather_agent.py 使用)"""
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=MODEL,
        openai_api_key=API_KEY,
        openai_api_base=BASE_URL + "/v1",
        temperature=0.7,
    )