"""
Cryptographic utilities for secure API key embedding.
"""

import base64
import hashlib
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SecureKeyManager:
    """Manages secure encryption/decryption of embedded API keys."""
    
    def __init__(self):
        # Use a combination of system-specific data for key derivation
        self._salt = self._get_deterministic_salt()
        self._key = self._derive_key()
    
    def _get_deterministic_salt(self) -> bytes:
        """Generate a deterministic salt based on system characteristics."""
        # Use a combination of fixed and semi-fixed system data
        base_data = "gsai-secure-keys-v1.0"
        
        # Add some system-specific but deterministic data
        try:
            # Use the application's directory path as part of salt
            import sys
            app_path = os.path.dirname(os.path.abspath(sys.argv[0]))
            system_data = f"{base_data}-{app_path}"
        except:
            system_data = base_data
        
        # Create a deterministic salt
        return hashlib.sha256(system_data.encode()).digest()[:16]
    
    def _derive_key(self) -> bytes:
        """Derive encryption key from deterministic salt."""
        password = b"gsai-embedded-key-protection-2024"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_key(self, api_key: str) -> str:
        """Encrypt an API key for embedding."""
        if not api_key or not api_key.strip():
            return ""
        
        fernet = Fernet(self._key)
        encrypted = fernet.encrypt(api_key.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt an embedded API key."""
        if not encrypted_key or not encrypted_key.strip():
            return ""
        
        try:
            fernet = Fernet(self._key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_key.encode())
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception:
            # If decryption fails, return empty string (graceful degradation)
            return ""
    
    def is_encrypted_key(self, key_value: str) -> bool:
        """Check if a key value appears to be encrypted."""
        if not key_value or not key_value.strip():
            return False
        
        # Encrypted keys will be base64 encoded and longer than typical API keys
        try:
            # Try to decode as base64
            base64.urlsafe_b64decode(key_value.encode())
            # If it's much longer than a typical API key, likely encrypted
            return len(key_value) > 100
        except:
            return False


# Global instance
_key_manager = SecureKeyManager()


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key for secure embedding."""
    return _key_manager.encrypt_key(api_key)


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an embedded API key."""
    return _key_manager.decrypt_key(encrypted_key)


def is_encrypted_key(key_value: str) -> bool:
    """Check if a key value is encrypted."""
    return _key_manager.is_encrypted_key(key_value)


def get_decrypted_key(key_value: str) -> str:
    """Get the decrypted version of a key (handles both encrypted and plain keys)."""
    if is_encrypted_key(key_value):
        return decrypt_api_key(key_value)
    return key_value