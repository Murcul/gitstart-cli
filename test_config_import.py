#!/usr/bin/env python3
"""
Test the config import logic specifically.
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config_import_logic():
    """Test the exact import logic from config.py."""
    try:
        # First, create a test production config
        from gsai.crypto_utils import encrypt_api_key
        
        test_openai = "sk-config-import-test"
        test_anthropic = "anthropic-config-import-test"
        
        encrypted_openai = encrypt_api_key(test_openai)
        encrypted_anthropic = encrypt_api_key(test_anthropic)
        
        config_content = f'''"""Test config for import testing"""
EMBEDDED_OPENAI_API_KEY = "{encrypted_openai}"
EMBEDDED_ANTHROPIC_API_KEY = "{encrypted_anthropic}"
BUILD_TYPE = "production"
BUILD_TIMESTAMP = "2025-06-19T21:45:00Z"
BUILD_COMMIT_SHA = "test123"
'''
        
        config_path = project_root / "gsai" / "build_config.py"
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print("✅ Created test config with encrypted keys")
        print(f"   OpenAI: {test_openai} -> {encrypted_openai[:30]}...")
        print(f"   Anthropic: {test_anthropic} -> {encrypted_anthropic[:30]}...")
        
        # Now test the exact logic from config.py
        print("\n🔍 Testing import logic:")
        
        try:
            print("Attempting imports...")
            from gsai.build_config import EMBEDDED_OPENAI_API_KEY, EMBEDDED_ANTHROPIC_API_KEY
            print(f"✅ Build config imported")
            print(f"   EMBEDDED_OPENAI_API_KEY: {EMBEDDED_OPENAI_API_KEY[:30]}...")
            print(f"   EMBEDDED_ANTHROPIC_API_KEY: {EMBEDDED_ANTHROPIC_API_KEY[:30]}...")
            
            from gsai.crypto_utils import get_decrypted_key
            print(f"✅ Crypto utils imported")
            
            # Decrypt embedded keys if they exist
            DECRYPTED_OPENAI_KEY = get_decrypted_key(EMBEDDED_OPENAI_API_KEY) if EMBEDDED_OPENAI_API_KEY else ''
            DECRYPTED_ANTHROPIC_KEY = get_decrypted_key(EMBEDDED_ANTHROPIC_API_KEY) if EMBEDDED_ANTHROPIC_API_KEY else ''
            
            print(f"✅ Decryption completed")
            print(f"   DECRYPTED_OPENAI_KEY: {DECRYPTED_OPENAI_KEY}")
            print(f"   DECRYPTED_ANTHROPIC_KEY: {DECRYPTED_ANTHROPIC_KEY}")
            
            # Check if decryption worked
            openai_correct = DECRYPTED_OPENAI_KEY == test_openai
            anthropic_correct = DECRYPTED_ANTHROPIC_KEY == test_anthropic
            
            print(f"   OpenAI correct: {openai_correct}")
            print(f"   Anthropic correct: {anthropic_correct}")
            
            if openai_correct and anthropic_correct:
                print("🎉 Config import logic works perfectly!")
                return True
            else:
                print("❌ Decryption didn't work correctly")
                return False
                
        except ImportError as e:
            print(f"❌ ImportError caught: {e}")
            EMBEDDED_OPENAI_API_KEY = ''
            EMBEDDED_ANTHROPIC_API_KEY = ''
            DECRYPTED_OPENAI_KEY = ''
            DECRYPTED_ANTHROPIC_KEY = ''
            print("   Fell back to empty strings")
            return False
        except Exception as e:
            print(f"❌ Other exception caught: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # Clean up
            config_path.unlink()
            
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_py_directly():
    """Test importing from the actual config.py file."""
    try:
        # Create test config
        from gsai.crypto_utils import encrypt_api_key
        
        test_openai = "sk-direct-config-test"
        encrypted_openai = encrypt_api_key(test_openai)
        
        config_content = f'''"""Direct config test"""
EMBEDDED_OPENAI_API_KEY = "{encrypted_openai}"
EMBEDDED_ANTHROPIC_API_KEY = ""
BUILD_TYPE = "production"
BUILD_TIMESTAMP = "2025-06-19T21:45:00Z"
BUILD_COMMIT_SHA = "test123"
'''
        
        config_path = project_root / "gsai" / "build_config.py"
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print("\n🔍 Testing direct import from config.py:")
        
        # Clear module cache to force fresh import
        modules_to_clear = [name for name in sys.modules.keys() if name.startswith('gsai')]
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]
        
        # Now try to import the config variables
        try:
            from gsai.config import DECRYPTED_OPENAI_KEY, DECRYPTED_ANTHROPIC_KEY
            
            print(f"✅ Successfully imported from config.py")
            print(f"   DECRYPTED_OPENAI_KEY: {DECRYPTED_OPENAI_KEY}")
            print(f"   DECRYPTED_ANTHROPIC_KEY: {DECRYPTED_ANTHROPIC_KEY}")
            
            success = DECRYPTED_OPENAI_KEY == test_openai and DECRYPTED_ANTHROPIC_KEY == ""
            
            if success:
                print("🎉 Direct config.py import works!")
            else:
                print("❌ Direct config.py import values incorrect")
                
            return success
            
        except Exception as e:
            print(f"❌ Failed to import from config.py: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            config_path.unlink()
            
    except Exception as e:
        print(f"❌ Direct config test failed: {e}")
        return False


if __name__ == "__main__":
    print("🔍 CONFIG IMPORT TEST")
    print("=" * 40)
    
    test1 = test_config_import_logic()
    test2 = test_config_py_directly()
    
    print("\n" + "=" * 40)
    if test1 and test2:
        print("🎉 CONFIG IMPORT WORKS!")
        print("✅ The issue must be elsewhere")
    else:
        print("❌ CONFIG IMPORT HAS ISSUES!")
        print("🔧 This explains why keys aren't available")
    
    sys.exit(0 if (test1 and test2) else 1)