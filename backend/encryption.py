"""
API Key 加解密模块

使用 Fernet 对称加密保护 API Key 存储安全。

流程:
- 首次启动: 自动生成 FERNET_KEY → 写入 .env
- 存储: api_key_db = encrypt(plaintext)
- 读取: plaintext = decrypt(api_key_db)
- 展示: mask_key(plaintext) → "sk-...abc1"
"""
import os
import logging
from pathlib import Path

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

ENV_PATH = Path(__file__).parent.parent / ".env"
FERNET_KEY_ENV = "FERNET_KEY"

_cipher: Fernet | None = None


def _find_env_line(key: str) -> int | None:
    """在 .env 中查找指定 key 所在行号，不存在返回 None"""
    if not ENV_PATH.exists():
        return None
    lines = ENV_PATH.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            return i
    return None


def _ensure_fernet_key() -> str:
    """确保 FERNET_KEY 存在，不存在则自动生成并写入 .env"""
    key = os.getenv(FERNET_KEY_ENV, "").strip()
    if key:
        return key

    # 尝试从 .env 文件读取
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            if line.startswith(f"{FERNET_KEY_ENV}="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                if key:
                    os.environ[FERNET_KEY_ENV] = key
                    return key

    # 自动生成
    key = Fernet.generate_key().decode()
    os.environ[FERNET_KEY_ENV] = key

    env_content = ""
    if ENV_PATH.exists():
        env_content = ENV_PATH.read_text(encoding="utf-8").rstrip()

    if env_content and not env_content.endswith("\n"):
        env_content += "\n"
    env_content += f"\n# 模型 API Key 加密密钥（自动生成，请勿修改）\n{FERNET_KEY_ENV}={key}\n"
    ENV_PATH.write_text(env_content, encoding="utf-8")
    logger.info(f"已自动生成 {FERNET_KEY_ENV} 并写入 .env")

    return key


def _get_cipher() -> Fernet:
    """懒加载 Fernet cipher 实例"""
    global _cipher
    if _cipher is None:
        key = _ensure_fernet_key()
        _cipher = Fernet(key.encode())
    return _cipher


def encrypt(plaintext: str) -> str:
    """加密明文 API Key → 密文"""
    if not plaintext:
        return ""
    return _get_cipher().encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    """解密密文 → 明文 API Key"""
    if not ciphertext:
        return ""
    try:
        return _get_cipher().decrypt(ciphertext.encode()).decode()
    except Exception:
        logger.warning("API Key 解密失败，可能 FERNET_KEY 已变更")
        return ""


def mask_key(plaintext: str) -> str:
    """脱敏展示：仅显示后 4 位，如 'sk-...abc1'"""
    if not plaintext:
        return ""
    if len(plaintext) <= 8:
        return plaintext[:2] + "***" + plaintext[-2:]
    return plaintext[:4] + "..." + plaintext[-4:]
