#!/usr/bin/env python3
"""
Debug crypto consistency issues.
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_crypto_consistency():
    """Test if crypto is consistent across multiple calls."""
    try:
        from gsai.crypto_utils import SecureKeyManager, encrypt_api_key, decrypt_api_key
        
        test_key = "sk-consistency-test"
        
        print("🔍 Testing crypto consistency:")
        print(f"Test key: {test_key}")
        
        # Test with direct manager
        manager1 = SecureKeyManager()
        encrypted1 = manager1.encrypt_key(test_key)
        print(f"Manager 1 encrypted: {encrypted1[:50]}...")
        
        decrypted1 = manager1.decrypt_key(encrypted1)
        print(f"Manager 1 decrypted: {decrypted1}")
        print(f"Manager 1 round trip: {test_key == decrypted1}")
        
        # Test with second manager (should be same)
        manager2 = SecureKeyManager()
        decrypted2 = manager2.decrypt_key(encrypted1)
        print(f"Manager 2 decrypted: {decrypted2}")
        print(f"Manager 2 round trip: {test_key == decrypted2}")
        
        # Test with global functions
        encrypted3 = encrypt_api_key(test_key)
        print(f"Global function encrypted: {encrypted3[:50]}...")
        
        decrypted3 = decrypt_api_key(encrypted3)
        print(f"Global function decrypted: {decrypted3}")
        print(f"Global function round trip: {test_key == decrypted3}")
        
        # Cross-test: encrypt with manager, decrypt with global
        decrypted4 = decrypt_api_key(encrypted1)
        print(f"Cross-test decrypted: {decrypted4}")
        print(f"Cross-test round trip: {test_key == decrypted4}")
        
        # Test the salt generation
        salt1 = manager1._get_deterministic_salt()
        salt2 = manager2._get_deterministic_salt()
        print(f"Salt 1: {salt1.hex()}")
        print(f"Salt 2: {salt2.hex()}")
        print(f"Salts match: {salt1 == salt2}")
        
        # Test key derivation
        key1 = manager1._derive_key()
        key2 = manager2._derive_key()
        print(f"Key 1: {key1[:20]}")
        print(f"Key 2: {key2[:20]}")
        print(f"Keys match: {key1 == key2}")
        
        return all([
            test_key == decrypted1,
            test_key == decrypted2,
            test_key == decrypted3,
            test_key == decrypted4,
            salt1 == salt2,
            key1 == key2
        ])
        
    except Exception as e:
        print(f"❌ Consistency test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_app_path_issue():
    """Test if the app path in salt generation is causing issues."""
    try:
        print("\n🔍 Testing app path salt generation:")
        
        from gsai.crypto_utils import SecureKeyManager
        
        # Create manager and show salt generation details
        manager = SecureKeyManager()
        
        # Manually recreate the salt logic to debug
        import os
        import hashlib
        import sys
        
        base_data = "gsai-secure-keys-v1.0"
        
        try:
            app_path = os.path.dirname(os.path.abspath(sys.argv[0]))
            system_data = f"{base_data}-{app_path}"
            print(f"App path: {app_path}")
            print(f"System data: {system_data}")
        except:
            system_data = base_data
            print(f"Fallback system data: {system_data}")
        
        salt = hashlib.sha256(system_data.encode()).digest()[:16]
        print(f"Generated salt: {salt.hex()}")
        
        # Compare with manager's salt
        manager_salt = manager._get_deterministic_salt()
        print(f"Manager salt: {manager_salt.hex()}")
        print(f"Salts match: {salt == manager_salt}")
        
        # The issue might be that sys.argv[0] is different during testing vs runtime
        print(f"sys.argv[0]: {sys.argv[0]}")
        print(f"__file__: {__file__}")
        
        return True
        
    except Exception as e:
        print(f"❌ App path test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🔍 CRYPTO CONSISTENCY DEBUG")
    print("=" * 50)
    
    test1 = test_crypto_consistency()
    test2 = test_app_path_issue()
    
    print("\n" + "=" * 50)
    if test1 and test2:
        print("✅ Crypto system is consistent")
    else:
        print("❌ Crypto system has consistency issues")
        print("🔧 This explains why keys aren't working in production")