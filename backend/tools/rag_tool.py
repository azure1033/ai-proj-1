"""
RAG 知识库核心引擎

提供:
- 文档向量化与存储 (ChromaDB)
- 中文语义检索
- 会话级隔离 (每会话独立 Collection)
- 文档增删管理
- 嵌入模型懒加载
"""

import contextvars
import json
import logging
from pathlib import Path
from typing import Optional

from langchain.tools import BaseTool
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from model_config import get_embedding_function, EMBEDDING_PROVIDER

logger = logging.getLogger(__name__)

# ==================== 路径常量 ====================

CHROMA_PERSIST_DIR = str(Path(__file__).parent.parent / "chroma_db")
RAG_SETTINGS_FILE = Path(__file__).parent.parent / "rag_settings.json"

# ==================== 默认设置 ====================

DEFAULT_SETTINGS: dict = {
    "embedding_provider": "zhipu",
    "embedding_model": "embedding-2",
    "chunk_size": 384,
    "chunk_overlap": 64,
    "retrieval_k": 4,
}

# ==================== 嵌入模型（委托给 model_config） ====================


def get_embeddings():
    """获取嵌入模型实例（委托给 model_config.get_embedding_function）

    Returns:
        Embeddings: 当前 Provider 的嵌入模型实例
    """
    return get_embedding_function()


# ==================== 中文文本分割器 ====================


def get_text_splitter(
    chunk_size: int = 384, chunk_overlap: int = 64
) -> RecursiveCharacterTextSplitter:
    """创建面向中文文档的递归文本分割器

    按中文标点优先级逐级切割，确保语义单元不被截断。
    分隔符顺序：段落 → 换行 → 句号 → 感叹号 → 问号 → 分号 → 逗号 → 顿号 → 空格 → 字符。

    Args:
        chunk_size: 文本块最大长度，默认 384
        chunk_overlap: 相邻文本块重叠长度，默认 64

    Returns:
        RecursiveCharacterTextSplitter: 配置好的分割器
    """
    return RecursiveCharacterTextSplitter(
        separators=[
            "\n\n",
            "\n",
            "。",
            "！",
            "？",
            "；",
            "，",
            "、",
            " ",
            "",
        ],
        keep_separator="end",
        add_start_index=True,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )


# ==================== 会话上下文（contextvars） ====================

_current_session_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    "rag_session_id", default="default"
)


def set_rag_session(session_id: str) -> None:
    """设置当前 RAG 会话 ID

    在同一请求生命周期中，确保所有 RAG 操作使用同一会话上下文。
    应在 main.py 的 /ask 端点中，Agent 执行前调用。

    Args:
        session_id: 会话唯一标识
    """
    _current_session_id.set(session_id)


def get_rag_session() -> str:
    """获取当前 RAG 会话 ID

    Returns:
        str: 当前会话 ID，未设置时返回 "default" 作为兜底
    """
    return _current_session_id.get()


# ==================== 向量存储管理 ====================


def get_vector_store(session_id: str) -> Chroma:
    """获取或创建会话专属的 ChromaDB 向量存储

    每个会话使用独立 Collection，名称格式基于 session_id 和 Provider：
    - zhipu:    rag_{session_id}
    - local:    rag_{session_id}_local
    - siliconflow: rag_{session_id}_sf

    不同 Provider 的维度不同，使用不同 collection 避免混用。

    Args:
        session_id: 会话唯一标识

    Returns:
        Chroma: 会话专属的向量存储实例
    """
    suffix = {"zhipu": "", "local": "_local", "siliconflow": "_sf"}.get(EMBEDDING_PROVIDER, "")
    collection_name = f"rag_{session_id}{suffix}"
    return Chroma(
        collection_name=collection_name,
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_PERSIST_DIR,
    )


# ==================== 文档摄入 ====================


def ingest_document(
    text: str,
    metadata: Optional[dict] = None,
    session_id: str = "",
) -> int:
    """将文本文档向量化并存入知识库

    对长文本自动分块、嵌入，存入当前会话的向量存储。
    分块策略使用中文感知的递归分割器。

    Args:
        text: 文档原始文本内容
        metadata: 文档元数据（来源、文件名、doc_id 等）
        session_id: 会话 ID，为空时从上下文自动获取

    Returns:
        int: 生成的文本块数量，失败返回 -1
    """
    try:
        sid = session_id or get_rag_session()
        doc = Document(page_content=text, metadata=metadata or {})
        splitter = get_text_splitter()
        chunks = splitter.split_documents([doc])

        if not chunks:
            logger.warning("文档分割后无有效文本块")
            return 0

        vector_store = get_vector_store(sid)
        vector_store.add_documents(chunks)

        logger.info(f"文档已入库: session={sid}, chunks={len(chunks)}")
        return len(chunks)
    except Exception as e:
        logger.error(f"文档摄入失败: {e}", exc_info=True)
        return -1


# ==================== 知识检索 ====================


def search_knowledge(
    query: str,
    session_id: str = "",
    k: int = 4,
) -> str:
    """从知识库中检索与查询最相关的文档片段

    使用向量语义相似度匹配，返回格式化后的检索结果。

    Args:
        query: 查询文本或关键词
        session_id: 会话 ID，为空时从上下文获取
        k: 返回的最相关片段数量，默认 4

    Returns:
        str: 格式化后的检索结果，包含来源和内容；
             向量存储为空时返回友好提示
    """
    try:
        sid = session_id or get_rag_session()
        vector_store = get_vector_store(sid)

        # 检查集合是否为空（collection 不存在或未添加文档）
        try:
            count = vector_store._collection.count()
        except Exception:
            count = 0

        if count == 0:
            return "当前知识库中暂无文档。请先上传文档后再查询。"

        docs = vector_store.similarity_search(query, k=k)

        if not docs:
            return "未找到与您问题相关的文档内容。请尝试更换查询关键词。"

        results = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get(
                "filename", doc.metadata.get("source", "未知来源")
            )
            results.append(f"[{i}] 来源: {source}")
            results.append(doc.page_content)
            results.append("-" * 40)

        return "\n".join(results)
    except Exception as e:
        logger.error(f"知识库检索失败: {e}", exc_info=True)
        return f"知识库检索出错: {str(e)}"


# ==================== 删除操作 ====================


def delete_document_vectors(doc_id: str, session_id: str) -> None:
    """删除指定文档的所有向量

    通过 metadata.doc_id 匹配并删除文档的所有分块向量。

    Args:
        doc_id: 文档唯一标识（对应 metadata 中的 doc_id 字段）
        session_id: 会话 ID
    """
    try:
        vector_store = get_vector_store(session_id)
        vector_store._collection.delete(where={"doc_id": doc_id})
        logger.info(f"已删除文档向量: doc_id={doc_id}, session={session_id}")
    except Exception as e:
        logger.error(f"删除文档向量失败: {e}", exc_info=True)


def delete_session_collection(session_id: str) -> None:
    """删除整个会话的知识库集合

    删除会话对应的 ChromaDB Collection 及其所有向量数据。

    Args:
        session_id: 会话 ID
    """
    try:
        vector_store = get_vector_store(session_id)
        vector_store.delete_collection()
        logger.info(f"已删除会话集合: session={session_id}")
    except Exception as e:
        logger.error(f"删除会话集合失败: {e}", exc_info=True)


# ==================== LangChain Tool ====================


class RAGSearchTool(BaseTool):
    """知识库检索工具 —— 从已上传文档中查找相关内容"""

    name: str = "search_knowledge_base"
    description: str = (
        "从知识库中检索与用户问题相关的文档内容。"
        "当用户询问已上传文档中的内容，或需要查找特定知识点时使用此工具。"
        "输入应为查询关键词或问题。"
    )

    def _run(self, query: str) -> str:
        """同步执行知识库检索

        从 contextvars 读取当前会话 ID，调用 search_knowledge 进行语义检索。
        知识库为空时自动返回友好提示。

        Args:
            query: 用户查询关键词或问题

        Returns:
            str: 检索结果或友好提示
        """
        try:
            session_id = get_rag_session()
            return search_knowledge(query, session_id=session_id)
        except Exception as e:
            logger.error(f"RAG 工具执行失败: {e}", exc_info=True)
            return f"知识库查询失败: {str(e)}"

    async def _arun(self, query: str) -> str:
        """异步执行知识库检索（委托同步实现）"""
        return self._run(query)


# ==================== 工具工厂 ====================


def get_rag_tool() -> RAGSearchTool:
    """创建 RAG 知识库检索工具实例

    始终返回可用实例，即使当前无文档入库。
    工具在执行时自动检测空集合并返回友好提示，无需在工厂层做条件判断。

    Returns:
        RAGSearchTool: 可用的知识库检索工具
    """
    return RAGSearchTool()


# ==================== 设置管理 ====================


def load_rag_settings() -> dict:
    """从磁盘加载 RAG 设置

    读取 backend/rag_settings.json，文件不存在时返回默认设置。

    Returns:
        dict: 当前保存的设置字典
    """
    try:
        if RAG_SETTINGS_FILE.exists():
            with open(RAG_SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"加载 RAG 设置失败，使用默认值: {e}")
    return dict(DEFAULT_SETTINGS)


def save_rag_settings(settings: dict) -> None:
    """保存 RAG 设置到磁盘

    以 JSON 格式写入 backend/rag_settings.json。

    Args:
        settings: 要保存的设置字典
    """
    try:
        with open(RAG_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        logger.info("RAG 设置已保存")
    except Exception as e:
        logger.error(f"保存 RAG 设置失败: {e}", exc_info=True)
