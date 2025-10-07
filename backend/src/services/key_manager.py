"""API Key management service."""
from sqlalchemy.orm import Session
from typing import Optional, List
from ..models.api_key import APIKey, KeyStatus
from .encryption import get_encryption_service
from datetime import datetime


class KeyManager:
    """Manages API keys for providers."""

    def __init__(self):
        self.encryption = get_encryption_service()

    def add_key(self, db: Session, provider: str, api_key: str) -> APIKey:
        """Add a new API key."""
        encrypted = self.encryption.encrypt(api_key)

        db_key = APIKey(
            provider=provider,
            encrypted_key=encrypted,
            status=KeyStatus.ACTIVE,
        )
        db.add(db_key)
        db.commit()
        db.refresh(db_key)
        return db_key

    def get_key(self, db: Session, key_id: int) -> Optional[APIKey]:
        """Get an API key by ID."""
        return db.query(APIKey).filter(APIKey.id == key_id).first()

    def get_key_by_provider(self, db: Session, provider: str) -> Optional[APIKey]:
        """Get active API key for a provider."""
        return (
            db.query(APIKey)
            .filter(APIKey.provider == provider, APIKey.status == KeyStatus.ACTIVE)
            .first()
        )

    def list_keys(self, db: Session) -> List[APIKey]:
        """List all API keys."""
        return db.query(APIKey).filter(APIKey.status != KeyStatus.REVOKED).all()

    def decrypt_key(self, api_key: APIKey) -> str:
        """Decrypt an API key."""
        return self.encryption.decrypt(api_key.encrypted_key)

    def update_key_status(
        self, db: Session, key_id: int, status: KeyStatus
    ) -> Optional[APIKey]:
        """Update key status."""
        db_key = self.get_key(db, key_id)
        if db_key:
            db_key.status = status
            db_key.last_validated = datetime.utcnow()
            db.commit()
            db.refresh(db_key)
        return db_key

    def revoke_key(self, db: Session, key_id: int) -> bool:
        """Revoke an API key."""
        db_key = self.get_key(db, key_id)
        if db_key:
            db_key.status = KeyStatus.REVOKED
            db.commit()
            return True
        return False

    def delete_key(self, db: Session, key_id: int) -> bool:
        """Delete an API key permanently."""
        db_key = self.get_key(db, key_id)
        if db_key:
            db.delete(db_key)
            db.commit()
            return True
        return False


# Singleton instance
_key_manager = None


def get_key_manager() -> KeyManager:
    """Get key manager instance."""
    global _key_manager
    if _key_manager is None:
        _key_manager = KeyManager()
    return _key_manager
