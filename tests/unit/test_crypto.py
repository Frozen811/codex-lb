from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest
from cryptography.fernet import Fernet
from pydantic import ValidationError

from app.core.config.key_fingerprint import compute_encryption_key_fingerprint
from app.core.config.settings import Settings
from app.core.crypto import TokenEncryptor, get_or_create_key

pytestmark = pytest.mark.unit


def test_encryption_key_validation_accepts_valid_fernet_key() -> None:
    raw_key = Fernet.generate_key().decode("utf-8")
    settings = Settings(_env_file=None, encryption_key=raw_key)
    assert settings.encryption_key == raw_key


def test_encryption_key_validation_rejects_invalid_fernet_key() -> None:
    with pytest.raises(ValidationError, match="CODEX_LB_ENCRYPTION_KEY must be a valid 32-byte"):
        Settings(_env_file=None, encryption_key="not-a-valid-fernet-key")


def test_get_or_create_key_prefers_encryption_key_setting() -> None:
    raw_key = Fernet.generate_key().decode("utf-8")
    fake_settings = mock.MagicMock(spec=Settings)
    fake_settings.encryption_key = raw_key
    fake_settings.encryption_key_file = Path("/nonexistent/encryption.key")

    with mock.patch("app.core.crypto.get_settings", return_value=fake_settings):
        key = get_or_create_key()
        assert key == raw_key.encode("utf-8")


def test_get_or_create_key_explicit_key_file_takes_precedence(tmp_path: Path) -> None:
    file_key = Fernet.generate_key()
    key_file = tmp_path / "custom.key"
    key_file.write_bytes(file_key)

    raw_key = Fernet.generate_key().decode("utf-8")
    fake_settings = mock.MagicMock(spec=Settings)
    fake_settings.encryption_key = raw_key
    fake_settings.encryption_key_file = tmp_path / "default.key"

    with mock.patch("app.core.crypto.get_settings", return_value=fake_settings):
        key = get_or_create_key(key_file=key_file)
        assert key == file_key


def test_token_encryptor_roundtrip_with_raw_encryption_key() -> None:
    raw_key = Fernet.generate_key().decode("utf-8")
    fake_settings = mock.MagicMock(spec=Settings)
    fake_settings.encryption_key = raw_key
    fake_settings.encryption_key_file = Path("/nonexistent/encryption.key")

    with mock.patch("app.core.crypto.get_settings", return_value=fake_settings):
        encryptor = TokenEncryptor()
        encrypted = encryptor.encrypt("secret-token-123")
        assert encryptor.decrypt(encrypted) == "secret-token-123"


def test_compute_fingerprint_with_raw_encryption_key() -> None:
    raw_key = Fernet.generate_key().decode("utf-8")
    fake_settings = mock.MagicMock(spec=Settings)
    fake_settings.encryption_key = raw_key
    fake_settings.encryption_key_file = Path("/nonexistent/encryption.key")

    with mock.patch("app.core.crypto.get_settings", return_value=fake_settings):
        fingerprint = compute_encryption_key_fingerprint()
        import hashlib

        expected = f"sha256:{hashlib.sha256(raw_key.encode('utf-8')).hexdigest()}"
        assert fingerprint == expected
