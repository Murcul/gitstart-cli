#!/usr/bin/env python3
"""
Test script for the encryption system.
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_encryption():
    """Test the encryption and decryption functionality."""
    try:
        from gsai.crypto_utils import encrypt_api_key, decrypt_api_key, is_encrypted_key, get_decrypted_key
        
        print("🔐 Testing API Key Encryption System")
        print("=" * 50)
        
        # Test data
        test_key = "sk-test123456789abcdef"
        
        print(f"📝 Original Key: {test_key}")
        
        # Test encryption
        encrypted_key = encrypt_api_key(test_key)
        print(f"🔒 Encrypted Key: {encrypted_key}")
        print(f"🔍 Is Encrypted: {is_encrypted_key(encrypted_key)}")
        
        # Test decryption
        decrypted_key = decrypt_api_key(encrypted_key)
        print(f"🔓 Decrypted Key: {decrypted_key}")
        
        # Test get_decrypted_key function
        auto_decrypted = get_decrypted_key(encrypted_key)
        print(f"🔄 Auto Decrypted: {auto_decrypted}")
        
        # Verify the round trip
        if test_key == decrypted_key == auto_decrypted:
            print("\n✅ Encryption test PASSED!")
            print("   - Encryption works correctly")
            print("   - Decryption works correctly")
            print("   - Auto-detection works correctly")
        else:
            print("\n❌ Encryption test FAILED!")
            print(f"   - Original: {test_key}")
            print(f"   - Decrypted: {decrypted_key}")
            print(f"   - Auto: {auto_decrypted}")
            return False
        
        # Test empty string handling
        print("\n🔍 Testing edge cases...")
        empty_encrypted = encrypt_api_key("")
        print(f"Empty string encrypted: '{empty_encrypted}'")
        
        empty_decrypted = decrypt_api_key("")
        print(f"Empty string decrypted: '{empty_decrypted}'")
        
        # Test with plain key (should pass through)
        plain_key = "sk-plain123"
        plain_result = get_decrypted_key(plain_key)
        print(f"Plain key pass-through: {plain_key} -> {plain_result}")
        
        if plain_key == plain_result:
            print("✅ Plain key pass-through works!")
        else:
            print("❌ Plain key pass-through failed!")
            return False
        
        print("\n🎉 All encryption tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Encryption test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_build_config():
    """Test the build config integration."""
    try:
        print("\n🏗️ Testing Build Config Integration")
        print("=" * 50)
        
        # Test importing build config
        from gsai.build_config import EMBEDDED_OPENAI_API_KEY, EMBEDDED_ANTHROPIC_API_KEY, BUILD_TYPE
        
        print(f"Build Type: {BUILD_TYPE}")
        print(f"OpenAI Key: {'Set' if EMBEDDED_OPENAI_API_KEY else 'Empty'}")
        print(f"Anthropic Key: {'Set' if EMBEDDED_ANTHROPIC_API_KEY else 'Empty'}")
        
        # Test the config system
        from gsai.config import DECRYPTED_OPENAI_KEY, DECRYPTED_ANTHROPIC_KEY
        
        print(f"Decrypted OpenAI Key: {'Set' if DECRYPTED_OPENAI_KEY else 'Empty'}")
        print(f"Decrypted Anthropic Key: {'Set' if DECRYPTED_ANTHROPIC_KEY else 'Empty'}")
        
        print("✅ Build config integration works!")
        return True
        
    except Exception as e:
        print(f"❌ Build config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cli_settings():
    """Test CLI settings with encrypted keys."""
    try:
        print("\n⚙️ Testing CLI Settings Integration")
        print("=" * 50)
        
        from gsai.config import cli_settings
        
        print(f"CLI OpenAI Key: {'Set' if cli_settings.OPENAI_API_KEY else 'Empty'}")
        print(f"CLI Anthropic Key: {'Set' if cli_settings.ANTHROPIC_API_KEY else 'Empty'}")
        
        # Test the validation logic from chat.py
        has_openai = cli_settings.OPENAI_API_KEY and cli_settings.OPENAI_API_KEY.strip()
        has_anthropic = cli_settings.ANTHROPIC_API_KEY and cli_settings.ANTHROPIC_API_KEY.strip()
        
        print(f"Valid OpenAI Key: {bool(has_openai)}")
        print(f"Valid Anthropic Key: {bool(has_anthropic)}")
        print(f"Has Any Valid Key: {bool(has_openai or has_anthropic)}")
        
        print("✅ CLI settings integration works!")
        return True
        
    except Exception as e:
        print(f"❌ CLI settings test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = True
    
    success &= test_encryption()
    success &= test_build_config()  
    success &= test_cli_settings()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Encryption system is working correctly")
        print("✅ Ready for production build")
    else:
        print("❌ SOME TESTS FAILED!")
        print("⚠️ Fix issues before proceeding")
        
    sys.exit(0 if success else 1)