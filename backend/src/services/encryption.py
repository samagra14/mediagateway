"""Encryption service for API keys."""
from cryptography.fernet import Fernet
from ..config import get_settings
import base64
import hashlib


class EncryptionService:
    """Service for encrypting and decrypting API keys."""

    def __init__(self):
        settings = get_settings()
        # Derive a valid Fernet key from the encryption key
        key = hashlib.sha256(settings.encryption_key.encode()).digest()
        self.cipher = Fernet(base64.urlsafe_b64encode(key))

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string."""
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a string."""
        return self.cipher.decrypt(ciphertext.encode()).decode()


# Singleton instance
_encryption_service = None


def get_encryption_service() -> EncryptionService:
    """Get encryption service instance."""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service
