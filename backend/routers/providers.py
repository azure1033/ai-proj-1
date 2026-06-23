"""Providers router — /providers CRUD, activate, test."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from encryption import decrypt as _decrypt_key, encrypt, mask_key
from models import ModelProvider, ProviderType
from provider_manager import get_provider_manager
from schemas.providers import (
    ProviderCreateRequest,
    ProviderTestCustomRequest,
    ProviderTestRequest,
    ProviderUpdateRequest,
)
from sqlalchemy import select

router = APIRouter(tags=["Providers"])


@router.get("/providers")
async def list_providers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ModelProvider).order_by(ModelProvider.provider_type, ModelProvider.id))
    providers = result.scalars().all()

    llm_list, emb_list = [], []
    for p in providers:
        item = {
            "id": p.id, "name": p.name, "provider_type": p.provider_type.value,
            "base_url": p.base_url,
            "api_key": mask_key(_decrypt_key(p.api_key)) if p.api_key else "",
            "model_name": p.model_name,
            "is_active": p.is_active, "is_preset": p.is_preset, "is_local": p.is_local,
        }
        if p.provider_type.value == "llm":
            llm_list.append(item)
        else:
            emb_list.append(item)
    return {"llm": llm_list, "embedding": emb_list}


@router.post("/providers")
async def create_provider(request: ProviderCreateRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.get(ModelProvider, request.id)
    if existing:
        raise HTTPException(status_code=400, detail=f"Provider ID '{request.id}' 已存在")

    provider_type = ProviderType.llm if request.provider_type == "llm" else ProviderType.embedding
    provider = ModelProvider(
        id=request.id, name=request.name, provider_type=provider_type,
        base_url=request.base_url, api_key=encrypt(request.api_key) if request.api_key else "",
        model_name=request.model_name, is_active=False, is_preset=False, is_local=False,
    )
    db.add(provider)
    await db.flush()
    return {"id": provider.id, "name": provider.name, "message": "创建成功"}


@router.put("/providers/{provider_id}")
async def update_provider(provider_id: str, request: ProviderUpdateRequest, db: AsyncSession = Depends(get_db)):
    provider = await db.get(ModelProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider 不存在")

    if provider.is_preset:
        if request.api_key is not None:
            provider.api_key = encrypt(request.api_key)
        if request.name is not None or request.base_url is not None or request.model_name is not None:
            raise HTTPException(status_code=400, detail="预设 provider 只能修改 API Key")
    else:
        if request.name is not None:
            provider.name = request.name
        if request.base_url is not None:
            provider.base_url = request.base_url
        if request.api_key is not None:
            provider.api_key = encrypt(request.api_key)
        if request.model_name is not None:
            provider.model_name = request.model_name

    await db.flush()
    await get_provider_manager().reload_from_db(db)
    return {"id": provider.id, "message": "更新成功"}


@router.delete("/providers/{provider_id}")
async def delete_provider(provider_id: str, db: AsyncSession = Depends(get_db)):
    provider = await db.get(ModelProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider 不存在")
    if provider.is_preset:
        raise HTTPException(status_code=400, detail="预设 provider 不可删除")
    await db.delete(provider)
    await db.flush()
    return {"id": provider_id, "message": "已删除"}


@router.post("/providers/{provider_id}/activate")
async def activate_provider(provider_id: str, db: AsyncSession = Depends(get_db)):
    from encryption import decrypt

    provider = await db.get(ModelProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider 不存在")
    if not provider.is_local:
        api_key = decrypt(provider.api_key) or ""
        if not api_key.strip():
            raise HTTPException(status_code=400, detail="请先设置 API Key 再激活该 Provider")

    success = await get_provider_manager().switch_provider(provider_id, db)
    if not success:
        raise HTTPException(status_code=500, detail="激活失败")
    return {"id": provider_id, "message": "已激活，即时生效"}


@router.post("/providers/{provider_id}/test")
async def test_provider(provider_id: str, request: ProviderTestRequest | None = None, db: AsyncSession = Depends(get_db)):
    override_key = request.api_key if request and request.api_key else None
    result = await get_provider_manager().test_connection(provider_id, db, api_key_override=override_key)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "连接失败"))
    return result


@router.post("/providers/test-custom")
async def test_custom_provider(request: ProviderTestCustomRequest):
    import httpx

    api_key = request.api_key or ""
    base_url = request.base_url.rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            headers = {}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            resp = await client.get(f"{base_url}/models", headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                count = len(data.get("data", []))
                return {"success": True, "model_count": count, "message": f"连接成功，发现 {count} 个模型"}
            else:
                raise HTTPException(status_code=400, detail=f"HTTP {resp.status_code}: {resp.text[:200]}")
    except httpx.TimeoutException:
        raise HTTPException(status_code=400, detail="连接超时（5s）")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
