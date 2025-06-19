#!/usr/bin/env python3
"""
Test the lightweight embedded keys module.
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_lightweight_module():
    """Test the lightweight embedded keys module."""
    try:
        # Create test config
        from gsai.crypto_utils import encrypt_api_key
        
        test_openai = "sk-lightweight-test"
        test_anthropic = "anthropic-lightweight-test"
        
        encrypted_openai = encrypt_api_key(test_openai)
        encrypted_anthropic = encrypt_api_key(test_anthropic)
        
        config_content = f'''"""Lightweight test config"""
EMBEDDED_OPENAI_API_KEY = "{encrypted_openai}"
EMBEDDED_ANTHROPIC_API_KEY = "{encrypted_anthropic}"
BUILD_TYPE = "production"
BUILD_TIMESTAMP = "2025-06-19T21:50:00Z"
BUILD_COMMIT_SHA = "test123"
'''
        
        config_path = project_root / "gsai" / "build_config.py"
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print("✅ Created test config")
        
        # Test the lightweight module
        from gsai.embedded_keys import get_api_keys, has_embedded_keys, is_production_build
        
        keys = get_api_keys()
        print(f"Keys: {keys}")
        
        print(f"Has embedded keys: {has_embedded_keys()}")
        print(f"Is production build: {is_production_build()}")
        
        success = (
            keys['openai'] == test_openai and
            keys['anthropic'] == test_anthropic and
            keys['build_type'] == 'production' and
            has_embedded_keys() and
            is_production_build()
        )
        
        if success:
            print("🎉 Lightweight module works perfectly!")
        else:
            print("❌ Lightweight module failed")
        
        # Clean up
        config_path.unlink()
        
        return success
        
    except Exception as e:
        print(f"❌ Lightweight module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_integration():
    """Test integration with the main config system."""
    try:
        # Create test config
        from gsai.crypto_utils import encrypt_api_key
        
        test_openai = "sk-config-integration-test"
        encrypted_openai = encrypt_api_key(test_openai)
        
        config_content = f'''"""Config integration test"""
EMBEDDED_OPENAI_API_KEY = "{encrypted_openai}"
EMBEDDED_ANTHROPIC_API_KEY = ""
BUILD_TYPE = "production"
BUILD_TIMESTAMP = "2025-06-19T21:50:00Z"
BUILD_COMMIT_SHA = "test123"
'''
        
        config_path = project_root / "gsai" / "build_config.py"
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print("\n🔍 Testing config integration:")
        
        # Clear module cache
        modules_to_clear = [name for name in sys.modules.keys() if name.startswith('gsai')]
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]
        
        # Test importing just the key variables
        try:
            from gsai.config import DECRYPTED_OPENAI_KEY, DECRYPTED_ANTHROPIC_KEY
            
            print(f"✅ Config import successful")
            print(f"   DECRYPTED_OPENAI_KEY: {DECRYPTED_OPENAI_KEY}")
            print(f"   DECRYPTED_ANTHROPIC_KEY: {DECRYPTED_ANTHROPIC_KEY}")
            
            success = DECRYPTED_OPENAI_KEY == test_openai and DECRYPTED_ANTHROPIC_KEY == ""
            
            if success:
                print("🎉 Config integration works!")
            else:
                print("❌ Config integration failed")
            
            return success
            
        except Exception as e:
            print(f"❌ Config integration failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            config_path.unlink()
            
    except Exception as e:
        print(f"❌ Config integration test setup failed: {e}")
        return False


if __name__ == "__main__":
    print("🔍 LIGHTWEIGHT KEYS TEST")
    print("=" * 40)
    
    test1 = test_lightweight_module()
    test2 = test_config_integration()
    
    print("\n" + "=" * 40)
    if test1 and test2:
        print("🎉 LIGHTWEIGHT KEYS WORK!")
        print("✅ Keys should be available in production builds")
        print("✅ No dependency issues with this approach")
    else:
        print("❌ LIGHTWEIGHT KEYS HAVE ISSUES!")
    
    sys.exit(0 if (test1 and test2) else 1)