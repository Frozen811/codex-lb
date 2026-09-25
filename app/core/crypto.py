from __future__ import annotations

from pathlib import Path

from cryptography.fernet import Fernet

from app.core.config.settings import get_settings


def _get_or_create_key(key_file: Path) -> bytes:
    key_file.parent.mkdir(parents=True, exist_ok=True)
    if key_file.exists():
        return key_file.read_bytes()
    key = Fernet.generate_key()
    key_file.write_bytes(key)
    key_file.chmod(0o600)
    return key


class TokenEncryptor:
    def __init__(self, key: bytes | None = None, key_file: Path | None = None) -> None:
        if key is not None:
            resolved_key = key
        elif key_file is not None:
            resolved_key = _get_or_create_key(key_file)
        else:
            settings = get_settings()
            if settings.encryption_key:
                resolved_key = settings.encryption_key.encode("utf-8")
            else:
                resolved_key = _get_or_create_key(settings.encryption_key_file)
        self._fernet = Fernet(resolved_key)

    def encrypt(self, token: str) -> bytes:
        return self._fernet.encrypt(token.encode())

    def decrypt(self, encrypted: bytes) -> str:
        return self._fernet.decrypt(encrypted).decode()


def get_or_create_key(key_file: Path | None = None) -> bytes:
    if key_file is not None:
        return _get_or_create_key(key_file)
    settings = get_settings()
    if settings.encryption_key:
        return settings.encryption_key.encode("utf-8")
    return _get_or_create_key(settings.encryption_key_file)
