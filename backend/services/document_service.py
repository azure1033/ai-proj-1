"""
Document service — upload, list, clear, delete documents with RAG ingestion.
"""
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from pypdf import PdfReader
import docx

from tools.rag_tool import set_rag_session, ingest_document, delete_document_vectors

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Session-keyed document registry: {session_id: [doc_dict, ...]}
_document_registry: dict[str, list[dict]] = {}


def _ensure_registry(session_id: str) -> list[dict]:
    if session_id not in _document_registry:
        _document_registry[session_id] = []
    return _document_registry[session_id]


def extract_text_from_file(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    if ext == ".txt":
        return file_path.read_text(encoding="utf-8", errors="ignore")
    if ext == ".pdf":
        reader = PdfReader(str(file_path))
        text = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text.append(page_text)
        return "\n\n".join(text)
    if ext == ".docx":
        doc = docx.Document(str(file_path))
        text = [p.text for p in doc.paragraphs]
        return "\n\n".join(text)
    raise ValueError(f"不支持的文件类型：{ext}")


def save_uploaded_file(upload_file: UploadFile) -> tuple[Path, str]:
    filename = Path(upload_file.filename or 'uploaded_file').name
    dest = UPLOAD_DIR / f"{uuid4().hex}_{filename}"
    with dest.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    upload_file.file.close()
    return dest, filename


def append_document(filename: str, text: str, session_id: str) -> dict:
    doc_id = uuid4().hex
    document = {
        "id": doc_id,
        "filename": filename,
        "text": text,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
    _ensure_registry(session_id).append(document)
    return document


def get_documents_context(session_id: str) -> str:
    docs = _ensure_registry(session_id)
    if not docs:
        return ""
    context_pieces = []
    for doc in docs:
        snippet = doc["text"]
        if len(snippet) > 6000:
            snippet = snippet[:6000] + "\n..."
        context_pieces.append(f"文件名：{doc['filename']}\n内容：{snippet}")
    return "\n\n".join(context_pieces)


def handle_document_query(query: str, session_id: str) -> str:
    from model_config import MODEL
    context = get_documents_context(session_id)
    prompt = (
        "你是一个智能助手。以下是用户上传的文档内容。请基于这些文档回答问题。"
        "如果文档中没有相关信息，请如实说明\n\n"
        f"文档内容：\n{context}\n\n用户问题：{query}\n"
        "请只基于文档内容作答，并在答案中说明引用自文档的部分。"
    )
    from provider_manager import get_provider_manager
    client = get_provider_manager().get_active_llm_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=700,
    )
    return (response.choices[0].message.content or "").strip()


async def upload_document(file: UploadFile, session_id: str) -> dict:
    """Upload a document, extract text, ingest to RAG, and register it."""
    dest, filename = save_uploaded_file(file)
    text = extract_text_from_file(dest)
    document = append_document(filename, text, session_id)
    try:
        set_rag_session(session_id)
        chunk_count = ingest_document(text, {"doc_id": document["id"], "filename": filename}, session_id)
        document["chunks"] = chunk_count if chunk_count >= 0 else 0
        document["indexed"] = chunk_count >= 0
    except Exception:
        document["chunks"] = 0
        document["indexed"] = False
    return {
        "id": document["id"],
        "filename": filename,
        "uploaded_at": document["uploaded_at"],
        "chunks": document.get("chunks", 0),
        "indexed": document.get("indexed", False),
    }


def list_documents(session_id: str) -> list[dict]:
    """List all documents for a session."""
    docs = _ensure_registry(session_id)
    return [{
        "id": d["id"],
        "filename": d["filename"],
        "uploaded_at": d["uploaded_at"],
        "chunks": d.get("chunks", 0),
        "indexed": d.get("indexed", False),
    } for d in docs]


def clear_documents(session_id: str) -> dict:
    """Clear all documents for a session."""
    if session_id in _document_registry:
        _document_registry[session_id] = []
    return {"status": "ok", "message": "文档已清空"}


async def delete_document(doc_id: str, session_id: str) -> dict:
    """Delete a single document and its RAG vectors."""
    docs = _ensure_registry(session_id)
    doc = next((d for d in docs if d["id"] == doc_id), None)
    if not doc:
        return None  # caller handles 404
    try:
        delete_document_vectors(doc_id, session_id)
    except Exception as e:
        logger.warning(f"删除文档向量失败: {e}")
    for f in UPLOAD_DIR.iterdir():
        if doc_id in f.name:
            f.unlink(missing_ok=True)
    _document_registry[session_id] = [d for d in docs if d["id"] != doc_id]
    return {"status": "ok", "message": "文档已删除", "doc_id": doc_id}
