#!/usr/bin/env python3
"""
Debug the decryption issue.
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def debug_issue():
    """Debug the decryption issue."""
    try:
        from gsai.crypto_utils import encrypt_api_key, get_decrypted_key
        
        # Test case: empty string
        print("Testing empty string handling:")
        empty_encrypted = encrypt_api_key("")
        print(f"Empty string encrypted: '{empty_encrypted}'")
        
        empty_decrypted = get_decrypted_key("")
        print(f"Empty string decrypted: '{empty_decrypted}'")
        
        # Test case: what happens when we store empty in config
        config_content = f'''"""Debug config"""
EMBEDDED_OPENAI_API_KEY = "Z0FBQUFBQm9WSVFKenhTWHJIeGhKQm1hS0pSSFIyeWl0YnpXQWN4VzctUGJ0dS1pV0QyRGlxQ2NFM3FjNHkyUGN3Z3hGb1ZHeEs4cGxCOUowVGpPeGNxc3k1cnhmcUtvcWNaaXlPZVg5Z09FQTA0ZElEQms9"
EMBEDDED_ANTHROPIC_API_KEY = ""
BUILD_TYPE = "production"
'''
        
        config_path = project_root / "gsai" / "build_config.py"
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        # Import and check
        from gsai.build_config import EMBEDDED_OPENAI_API_KEY, EMBEDDED_ANTHROPIC_API_KEY
        
        print(f"\nFrom config file:")
        print(f"EMBEDDED_OPENAI_API_KEY: '{EMBEDDED_OPENAI_API_KEY[:30]}...'")
        print(f"EMBEDDED_ANTHROPIC_API_KEY: '{EMBEDDED_ANTHROPIC_API_KEY}'")
        
        # Decrypt both
        openai_result = get_decrypted_key(EMBEDDED_OPENAI_API_KEY)
        anthropic_result = get_decrypted_key(EMBEDDED_ANTHROPIC_API_KEY)
        
        print(f"\nDecryption results:")
        print(f"OpenAI result: '{openai_result}'")
        print(f"Anthropic result: '{anthropic_result}'")
        
        # The issue might be module reloading - let's check
        print(f"\nModule reloading check:")
        
        # Remove the module from cache
        if 'gsai.build_config' in sys.modules:
            del sys.modules['gsai.build_config']
        
        # Import again
        from gsai.build_config import EMBEDDED_OPENAI_API_KEY as OPENAI2, EMBEDDED_ANTHROPIC_API_KEY as ANTHROPIC2
        
        print(f"Second import OpenAI: '{OPENAI2[:30]}...'")
        print(f"Second import Anthropic: '{ANTHROPIC2}'")
        
        # Decrypt again
        openai_result2 = get_decrypted_key(OPENAI2)
        anthropic_result2 = get_decrypted_key(ANTHROPIC2)
        
        print(f"Second decryption OpenAI: '{openai_result2}'")
        print(f"Second decryption Anthropic: '{anthropic_result2}'")
        
        # Clean up
        config_path.unlink()
        
    except Exception as e:
        print(f"Debug failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_issue()