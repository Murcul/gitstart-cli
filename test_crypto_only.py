#!/usr/bin/env python3
"""
Simple test script for just the crypto functionality.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_crypto_functionality():
    """Test only the crypto functions without dependencies."""
    try:
        from gsai.crypto_utils import encrypt_api_key, decrypt_api_key, is_encrypted_key, get_decrypted_key
        
        print("🔐 Testing API Key Encryption System")
        print("=" * 50)
        
        # Test various key types
        test_cases = [
            "sk-test123456789abcdef",
            "anthropic-key-123456789",
            "very-long-api-key-with-many-characters-for-testing-purposes-12345",
            "short-key",
            "",
        ]
        
        for i, test_key in enumerate(test_cases, 1):
            print(f"\n📝 Test Case {i}: '{test_key[:20]}{'...' if len(test_key) > 20 else ''}'")
            
            # Test encryption
            encrypted_key = encrypt_api_key(test_key)
            print(f"🔒 Encrypted: {encrypted_key[:30]}{'...' if len(encrypted_key) > 30 else ''}")
            
            # Test detection
            is_enc = is_encrypted_key(encrypted_key)
            print(f"🔍 Is Encrypted: {is_enc}")
            
            # Test decryption
            decrypted_key = decrypt_api_key(encrypted_key)
            print(f"🔓 Decrypted: '{decrypted_key[:20]}{'...' if len(decrypted_key) > 20 else ''}'")
            
            # Test auto-detection
            auto_decrypted = get_decrypted_key(encrypted_key)
            print(f"🔄 Auto Decrypted: '{auto_decrypted[:20]}{'...' if len(auto_decrypted) > 20 else ''}'")
            
            # Verify round trip
            if test_key == decrypted_key == auto_decrypted:
                print("✅ Round trip successful")
            else:
                print("❌ Round trip failed!")
                return False
        
        # Test plain key pass-through
        print(f"\n🔄 Testing plain key pass-through...")
        plain_key = "sk-plain-key-123"
        result = get_decrypted_key(plain_key)
        if plain_key == result:
            print("✅ Plain key pass-through works")
        else:
            print("❌ Plain key pass-through failed")
            return False
        
        print("\n🎉 ALL CRYPTO TESTS PASSED!")
        print("✅ Encryption system is ready for production")
        return True
        
    except Exception as e:
        print(f"\n❌ Crypto test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_build_config_mock():
    """Test build config functionality by simulating a production build."""
    try:
        print("\n🏗️ Testing Build Config with Mock Data")
        print("=" * 50)
        
        # Simulate encrypted keys
        from gsai.crypto_utils import encrypt_api_key
        
        mock_openai_key = "sk-mock-openai-key-123456789"
        mock_anthropic_key = "anthropic-mock-key-987654321"
        
        encrypted_openai = encrypt_api_key(mock_openai_key)
        encrypted_anthropic = encrypt_api_key(mock_anthropic_key)
        
        print(f"Mock OpenAI Key: {mock_openai_key}")
        print(f"Encrypted: {encrypted_openai[:50]}...")
        
        print(f"\nMock Anthropic Key: {mock_anthropic_key}")
        print(f"Encrypted: {encrypted_anthropic[:50]}...")
        
        # Test decryption
        from gsai.crypto_utils import get_decrypted_key
        
        decrypted_openai = get_decrypted_key(encrypted_openai)
        decrypted_anthropic = get_decrypted_key(encrypted_anthropic)
        
        print(f"\nDecrypted OpenAI: {decrypted_openai}")
        print(f"Decrypted Anthropic: {decrypted_anthropic}")
        
        if mock_openai_key == decrypted_openai and mock_anthropic_key == decrypted_anthropic:
            print("✅ Build config simulation successful")
            return True
        else:
            print("❌ Build config simulation failed")
            return False
        
    except Exception as e:
        print(f"❌ Build config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = True
    
    success &= test_crypto_functionality()
    success &= test_build_config_mock()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ The encrypted key embedding system is working correctly")
        print("✅ Ready for GitHub Actions build with embedded encrypted keys")
        print("✅ Users will be able to run 'gsai chat' without API key setup")
    else:
        print("❌ SOME TESTS FAILED!")
        print("⚠️ Fix issues before proceeding")
        
    sys.exit(0 if success else 1)