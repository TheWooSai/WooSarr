"""Secrets manager for WooSarr.

Provides encryption/decryption, key generation, rotation, and masking.
Uses AES-256-GCM for encryption. Master key stored in /config/secrets/master.key
with 0600 permissions.
"""
import os
import secrets
from pathlib import Path
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings


class SecretsManager:
    """Manages encryption keys and secret encryption/decryption."""

    def __init__(self, secrets_dir: Optional[Path] = None) -> None:
        self.secrets_dir = secrets_dir or settings.SECRETS_DIR

    def _ensure_secrets_dir(self) -> None:
        """Ensure secrets directory exists with correct permissions."""
        try:
            settings.SECRETS_DIR.mkdir(parents=True, exist_ok=True)
            os.chmod(settings.SECRETS_DIR, 0o700)
        except OSError:
            pass  # Directory may already exist or be read-only

    def generate_key(self) -> bytes:
        """Generate a new 256-bit (32-byte) AES key."""
        return AESGCM.generate_key(bit_length=256)

    def _load_master_key(self) -> bytes:
        """Load the master key from file, generating if it doesn't exist."""
        if not settings.MASTER_KEY_PATH.exists():
            self.rotate_key()
        with open(settings.MASTER_KEY_PATH, "rb") as f:
            return f.read()

    def rotate_key(self) -> bytes:
        """Generate a new master key and store it with 0600 permissions.

        Returns the new key.
        """
        self._ensure_secrets_dir()
        new_key = self.generate_key()
        with open(settings.MASTER_KEY_PATH, "wb") as f:
            f.write(new_key)
        os.chmod(settings.MASTER_KEY_PATH, 0o600)
        return new_key

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext string.

        Returns a hex-encoded string of the form: nonce:ciphertext:tag
        """
        key = self._load_master_key()
        aesgcm = AESGCM(key)
        nonce = secrets.token_bytes(12)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        return f"{nonce.hex()}:{ciphertext.hex()}"

    def decrypt(self, encrypted: str) -> str:
        """Decrypt an encrypted string.

        Expects hex-encoded string of the form: nonce:ciphertext:tag
        """
        key = self._load_master_key()
        aesgcm = AESGCM(key)
        parts = encrypted.split(":")
        if len(parts) != 2:
            raise ValueError("Invalid encrypted string format")
        nonce = bytes.fromhex(parts[0])
        ciphertext = bytes.fromhex(parts[1])
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode("utf-8")

    def mask(self, value: str, visible_chars: int = 4) -> str:
        """Mask a secret for display, showing only the last N characters.

        Example: mask("my-secret-token") -> "***********oken"
        """
        if len(value) <= visible_chars:
            return "*" * len(value)
        return "*" * (len(value) - visible_chars) + value[-visible_chars:]

    def store_secret(self, key: str, value: str) -> None:
        """Store an encrypted secret in the settings table."""
        from app.core.database import SessionLocal
        from app.models.settings import Settings as AppSettings

        encrypted = self.encrypt(value)
        db = SessionLocal()
        try:
            # Check if key already exists
            existing = db.query(AppSettings).filter(AppSettings.key == key).first()
            if existing:
                existing.value = encrypted
                existing.encrypted = True
            else:
                db.add(AppSettings(key=key, value=encrypted, encrypted=True))
            db.commit()
        finally:
            db.close()

    def get_secret(self, key: str) -> Optional[str]:
        """Retrieve and decrypt a secret from the settings table."""
        from app.core.database import SessionLocal
        from app.models.settings import Settings as AppSettings

        db = SessionLocal()
        try:
            setting = db.query(AppSettings).filter(AppSettings.key == key).first()
            if setting is None:
                return None
            if setting.encrypted:
                return self.decrypt(setting.value)
            return setting.value
        finally:
            db.close()

    def set(self, key: str, value: str) -> None:
        """Alias for store_secret."""
        self.store_secret(key, value)

    def get(self, key: str) -> Optional[str]:
        """Alias for get_secret."""
        return self.get_secret(key)

    def delete(self, key: str) -> None:
        """Alias for delete_secret."""
        self.delete_secret(key)

    def delete_secret(self, key: str) -> None:
        """Delete a secret from the settings table."""
        from app.core.database import SessionLocal
        from app.models.settings import Settings as AppSettings

        db = SessionLocal()
        try:
            setting = db.query(AppSettings).filter(AppSettings.key == key).first()
            if setting:
                db.delete(setting)
                db.commit()
        finally:
            db.close()