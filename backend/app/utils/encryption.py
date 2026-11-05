"""
Symmetric credential encryption utilities using cryptography.fernet.
"""

import base64
import hashlib
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

from app.config import get_settings


def _get_fernet_key() -> bytes:
    """
    Retrieve or derive a 32-byte URL-safe base64-encoded key.
    If ENCRYPTION_KEY is configured in settings, use that.
    Otherwise, derive a deterministic fallback key from SECRET_KEY.
    """
    settings = get_settings()
    configured_key = settings.ENCRYPTION_KEY.strip() if settings.ENCRYPTION_KEY else ""

    if configured_key:
        try:
            # Check if already a valid Fernet key
            Fernet(configured_key.encode())
            return configured_key.encode()
        except Exception:
            pass

    # Derive deterministic 32-byte Fernet key from SECRET_KEY
    seed = (settings.SECRET_KEY or "aashrays-pa-default-seed").encode("utf-8")
    digest = hashlib.sha256(seed).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_data(plain_text: str) -> str:
    """
    Encrypt a plaintext string using Fernet.
    Returns the ciphertext as an ASCII string.
    """
    if not plain_text:
        return ""
    key = _get_fernet_key()
    f = Fernet(key)
    encrypted_bytes = f.encrypt(plain_text.encode("utf-8"))
    return encrypted_bytes.decode("ascii")


def decrypt_data(cipher_text: Optional[str]) -> str:
    """
    Decrypt a Fernet ciphertext string.
    Returns plaintext string or empty string on failure/empty input.
    """
    if not cipher_text:
        return ""
    key = _get_fernet_key()
    f = Fernet(key)
    try:
        decrypted_bytes = f.decrypt(cipher_text.encode("ascii"))
        return decrypted_bytes.decode("utf-8")
    except InvalidToken:
        raise ValueError("Invalid or corrupted ciphertext, decryption failed.")

