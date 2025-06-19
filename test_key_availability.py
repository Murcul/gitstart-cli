#!/usr/bin/env python3
"""
Test just the key availability without full config system.
"""

import os
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_basic_crypto():
    """Test basic crypto functionality."""
    try:
        from gsai.crypto_utils import encrypt_api_key, decrypt_api_key, get_decrypted_key
        
        test_key = "sk-test123"
        encrypted = encrypt_api_key(test_key)
        decrypted = decrypt_api_key(encrypted)
        auto = get_decrypted_key(encrypted)
        
        print(f"✅ Crypto works: {test_key} -> {encrypted[:20]}... -> {decrypted}")
        return test_key == decrypted == auto
        
    except Exception as e:
        print(f"❌ Crypto failed: {e}")
        return False


def test_with_production_config():
    """Test with a production config file."""
    try:
        # Create test production config
        from gsai.crypto_utils import encrypt_api_key
        
        test_openai = "sk-prod-test-openai"
        test_anthropic = "anthropic-prod-test"
        
        encrypted_openai = encrypt_api_key(test_openai)
        encrypted_anthropic = encrypt_api_key(test_anthropic)
        
        # Write production config
        config_content = f'''"""Test production config"""
EMBEDDED_OPENAI_API_KEY = "{encrypted_openai}"
EMBEDDED_ANTHROPIC_API_KEY = "{encrypted_anthropic}"
BUILD_TYPE = "production"
BUILD_TIMESTAMP = "2025-06-19T21:40:00Z"
BUILD_COMMIT_SHA = "test123"
'''
        
        config_path = project_root / "gsai" / "build_config.py"
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print("✅ Created test production config")
        
        # Now test the decryption logic directly
        from gsai.build_config import EMBEDDED_OPENAI_API_KEY, EMBEDDED_ANTHROPIC_API_KEY
        from gsai.crypto_utils import get_decrypted_key
        
        decrypted_openai = get_decrypted_key(EMBEDDED_OPENAI_API_KEY)
        decrypted_anthropic = get_decrypted_key(EMBEDDED_ANTHROPIC_API_KEY)
        
        print(f"Embedded OpenAI: {EMBEDDED_OPENAI_API_KEY[:30]}...")
        print(f"Decrypted OpenAI: {decrypted_openai}")
        print(f"Expected OpenAI: {test_openai}")
        print(f"Match: {decrypted_openai == test_openai}")
        
        print(f"Embedded Anthropic: {EMBEDDED_ANTHROPIC_API_KEY[:30]}...")
        print(f"Decrypted Anthropic: {decrypted_anthropic}")
        print(f"Expected Anthropic: {test_anthropic}")
        print(f"Match: {decrypted_anthropic == test_anthropic}")
        
        success = (decrypted_openai == test_openai and decrypted_anthropic == test_anthropic)
        
        # Clean up
        config_path.unlink()
        
        return success
        
    except Exception as e:
        print(f"❌ Production config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_system_minimal():
    """Test the config system with minimal imports."""
    try:
        # Create a minimal test config
        from gsai.crypto_utils import encrypt_api_key
        
        test_key = "sk-minimal-test-key"
        encrypted_key = encrypt_api_key(test_key)
        
        # Write minimal config
        config_content = f'''"""Minimal test config"""
EMBEDDED_OPENAI_API_KEY = "{encrypted_key}"
EMBEDDED_ANTHROPIC_API_KEY = ""
BUILD_TYPE = "production"
BUILD_TIMESTAMP = "2025-06-19T21:40:00Z"
BUILD_COMMIT_SHA = "test123"
'''
        
        config_path = project_root / "gsai" / "build_config.py"
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        # Test the decryption import that config.py uses
        try:
            from gsai.build_config import EMBEDDED_OPENAI_API_KEY, EMBEDDED_ANTHROPIC_API_KEY
            from gsai.crypto_utils import get_decrypted_key
            
            decrypted_openai = get_decrypted_key(EMBEDDED_OPENAI_API_KEY)
            decrypted_anthropic = get_decrypted_key(EMBEDDED_ANTHROPIC_API_KEY)
            
            print(f"✅ Config import works")
            print(f"OpenAI: {encrypted_key[:30]}... -> {decrypted_openai}")
            print(f"Anthropic: '' -> '{decrypted_anthropic}'")
            
            success = (decrypted_openai == test_key and decrypted_anthropic == "")
            
            if success:
                print("✅ Config decryption works correctly")
            else:
                print("❌ Config decryption failed")
                
            # Clean up
            config_path.unlink()
            
            return success
            
        except Exception as e:
            print(f"❌ Config import failed: {e}")
            config_path.unlink()
            return False
            
    except Exception as e:
        print(f"❌ Minimal config test failed: {e}")
        return False


if __name__ == "__main__":
    print("🔍 KEY AVAILABILITY TEST")
    print("=" * 40)
    
    test1 = test_basic_crypto()
    print()
    
    test2 = test_with_production_config()
    print()
    
    test3 = test_config_system_minimal()
    print()
    
    print("=" * 40)
    if test1 and test2 and test3:
        print("🎉 ALL TESTS PASSED!")
        print("✅ The key system should work in production builds")
        print("✅ Keys are properly encrypted and decrypted")
        print("✅ Config system can import and use keys")
    else:
        print("❌ SOME TESTS FAILED!")
        print("⚠️ There may be issues with the key system")
        
    sys.exit(0 if (test1 and test2 and test3) else 1)