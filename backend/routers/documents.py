"""Documents router — /documents/upload, /documents, /documents/{doc_id}."""

from fastapi import APIRouter, File, HTTPException, UploadFile

from services.document_service import upload_document, list_documents, clear_documents, delete_document

router = APIRouter(tags=["Documents"])


@router.post("/documents/upload")
async def upload(file: UploadFile = File(...)):
    try:
        doc = upload_document(file, session_id="default")
        return doc
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.get("/documents")
async def list_all(session_id: str = "default"):
    return {"documents": list_documents(session_id)}


@router.delete("/documents")
async def clear_all():
    return clear_documents("default")


@router.delete("/documents/{doc_id}")
async def delete_one(doc_id: str):
    try:
        return delete_document(doc_id, "default")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
