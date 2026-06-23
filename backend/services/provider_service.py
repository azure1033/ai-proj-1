"""
Provider service — provider CRUD, activation, and testing logic extracted from main.py.
"""
import logging

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import ModelProvider, ProviderType
from encryption import encrypt as _encrypt_key, decrypt as _decrypt_key, mask_key
from provider_manager import get_provider_manager

logger = logging.getLogger(__name__)


async def list_providers(db: AsyncSession) -> dict:
    """List all providers with masked API keys, split by LLM/embedding."""
    result = await db.execute(select(ModelProvider).order_by(ModelProvider.provider_type, ModelProvider.id))
    providers = result.scalars().all()

    llm_list = []
    emb_list = []
    for p in providers:
        item = {
            "id": p.id,
            "name": p.name,
            "provider_type": p.provider_type.value,
            "base_url": p.base_url,
            "api_key": mask_key(_decrypt_key(p.api_key)) if p.api_key else "",
            "model_name": p.model_name,
            "is_active": p.is_active,
            "is_preset": p.is_preset,
            "is_local": p.is_local,
        }
        if p.provider_type.value == "llm":
            llm_list.append(item)
        else:
            emb_list.append(item)

    return {"llm": llm_list, "embedding": emb_list}


async def create_provider(
    provider_id: str,
    name: str,
    provider_type: str,
    base_url: str,
    api_key: str,
    model_name: str,
    db: AsyncSession,
) -> dict:
    """Create a new custom provider."""
    existing = await db.get(ModelProvider, provider_id)
    if existing:
        return None  # caller handles 400

    pt = ProviderType.llm if provider_type == "llm" else ProviderType.embedding
    encrypted_key = _encrypt_key(api_key) if api_key else ""

    provider = ModelProvider(
        id=provider_id,
        name=name,
        provider_type=pt,
        base_url=base_url,
        api_key=encrypted_key,
        model_name=model_name,
        is_active=False,
        is_preset=False,
        is_local=False,
    )
    db.add(provider)
    await db.flush()
    return {"id": provider.id, "name": provider.name, "message": "创建成功"}


async def update_provider(provider_id: str, request_data: dict, db: AsyncSession) -> dict:
    """Update a provider's configuration."""
    provider = await db.get(ModelProvider, provider_id)
    if not provider:
        return None  # caller handles 404

    if provider.is_preset:
        # preset: only api_key can be changed
        if request_data.get("api_key") is not None:
            provider.api_key = _encrypt_key(request_data["api_key"])
        if (request_data.get("name") is not None or
                request_data.get("base_url") is not None or
                request_data.get("model_name") is not None):
            return {"error": "预设 provider 只能修改 API Key"}
    else:
        if request_data.get("name") is not None:
            provider.name = request_data["name"]
        if request_data.get("base_url") is not None:
            provider.base_url = request_data["base_url"]
        if request_data.get("api_key") is not None:
            provider.api_key = _encrypt_key(request_data["api_key"])
        if request_data.get("model_name") is not None:
            provider.model_name = request_data["model_name"]

    await db.flush()
    await get_provider_manager().reload_from_db(db)
    return {"id": provider.id, "message": "更新成功"}


async def delete_provider(provider_id: str, db: AsyncSession) -> tuple[bool, str]:
    """Delete a custom provider (presets are rejected). Returns (success, message)."""
    provider = await db.get(ModelProvider, provider_id)
    if not provider:
        return False, "Provider 不存在"
    if provider.is_preset:
        return False, "预设 provider 不可删除"

    await db.delete(provider)
    await db.flush()
    return True, "已删除"


async def activate_provider(provider_id: str, db: AsyncSession) -> tuple[bool, str, dict | None]:
    """Activate a provider. Returns (success, message, result_dict)."""
    provider = await db.get(ModelProvider, provider_id)
    if not provider:
        return False, "Provider 不存在", None

    if not provider.is_local:
        api_key = _decrypt_key(provider.api_key) or ""
        if not api_key.strip():
            return False, "请先设置 API Key 再激活该 Provider", None

    success = await get_provider_manager().switch_provider(provider_id, db)
    if not success:
        return False, "激活失败", None
    return True, "已激活，即时生效", {"id": provider_id, "message": "已激活，即时生效"}


async def test_provider(provider_id: str, db: AsyncSession, api_key_override: str | None = None) -> dict:
    """Test a provider connection."""
    result = await get_provider_manager().test_connection(provider_id, db, api_key_override=api_key_override)
    return result


async def test_custom_provider(base_url: str, api_key: str) -> dict:
    """Test a custom provider connection without saving to DB."""
    base_url = base_url.rstrip("/")
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
                return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    except httpx.TimeoutException:
        return {"success": False, "error": "连接超时（5s）"}
    except Exception as e:
        return {"success": False, "error": str(e)}
