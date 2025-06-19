"""
Lightweight module for handling embedded API keys.
This module has minimal dependencies to avoid import issues.
"""

# Global variables for decrypted keys
DECRYPTED_OPENAI_KEY = ''
DECRYPTED_ANTHROPIC_KEY = ''
BUILD_TYPE = 'development'

def _load_embedded_keys():
    """Load and decrypt embedded keys if available."""
    global DECRYPTED_OPENAI_KEY, DECRYPTED_ANTHROPIC_KEY, BUILD_TYPE
    
    try:
        # Import build config
        from gsai.build_config import (
            EMBEDDED_OPENAI_API_KEY, 
            EMBEDDED_ANTHROPIC_API_KEY, 
            BUILD_TYPE as CONFIG_BUILD_TYPE
        )
        
        BUILD_TYPE = CONFIG_BUILD_TYPE
        
        # If we have embedded keys, try to decrypt them
        if EMBEDDED_OPENAI_API_KEY or EMBEDDED_ANTHROPIC_API_KEY:
            try:
                from gsai.crypto_utils import get_decrypted_key
                
                # Decrypt keys
                DECRYPTED_OPENAI_KEY = get_decrypted_key(EMBEDDED_OPENAI_API_KEY) if EMBEDDED_OPENAI_API_KEY else ''
                DECRYPTED_ANTHROPIC_KEY = get_decrypted_key(EMBEDDED_ANTHROPIC_API_KEY) if EMBEDDED_ANTHROPIC_API_KEY else ''
                
            except Exception:
                # If decryption fails, use keys as-is (might be plain text in dev builds)
                DECRYPTED_OPENAI_KEY = EMBEDDED_OPENAI_API_KEY
                DECRYPTED_ANTHROPIC_KEY = EMBEDDED_ANTHROPIC_API_KEY
                
    except ImportError:
        # No build config available - development environment
        pass

# Load keys when module is imported
_load_embedded_keys()

def get_api_keys():
    """Get the decrypted API keys."""
    return {
        'openai': DECRYPTED_OPENAI_KEY,
        'anthropic': DECRYPTED_ANTHROPIC_KEY,
        'build_type': BUILD_TYPE
    }

def has_embedded_keys():
    """Check if we have any embedded keys available."""
    return bool(DECRYPTED_OPENAI_KEY or DECRYPTED_ANTHROPIC_KEY)

def is_production_build():
    """Check if this is a production build."""
    return BUILD_TYPE == 'production'