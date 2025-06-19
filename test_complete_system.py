#!/usr/bin/env python3
"""
Test the complete encrypted key system end-to-end.
"""

import sys
import os
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_production_simulation():
    """Simulate a complete production environment."""
    try:
        print("🏭 SIMULATING PRODUCTION ENVIRONMENT")
        print("=" * 50)
        
        # Step 1: Create production config with encrypted keys
        from gsai.crypto_utils import encrypt_api_key
        
        prod_openai = "sk-prod-simulation-openai-key"
        prod_anthropic = "anthropic-prod-simulation-key"
        
        encrypted_openai = encrypt_api_key(prod_openai)
        encrypted_anthropic = encrypt_api_key(prod_anthropic)
        
        config_content = f'''"""Production simulation config"""
EMBEDDED_OPENAI_API_KEY = "{encrypted_openai}"
EMBEDDED_ANTHROPIC_API_KEY = "{encrypted_anthropic}"
BUILD_TYPE = "production"
BUILD_TIMESTAMP = "2025-06-19T22:00:00Z"
BUILD_COMMIT_SHA = "prod123456"
'''
        
        config_path = project_root / "gsai" / "build_config.py"
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print(f"✅ Created production config")
        print(f"   OpenAI: {prod_openai} -> encrypted")
        print(f"   Anthropic: {prod_anthropic} -> encrypted")
        
        # Step 2: Test embedded keys module
        print("\n🔍 Testing embedded keys module...")
        from gsai.embedded_keys import get_api_keys, has_embedded_keys, is_production_build
        
        keys = get_api_keys()
        print(f"   Keys loaded: OpenAI={bool(keys['openai'])}, Anthropic={bool(keys['anthropic'])}")
        print(f"   Has embedded keys: {has_embedded_keys()}")
        print(f"   Is production build: {is_production_build()}")
        
        embedded_correct = (
            keys['openai'] == prod_openai and
            keys['anthropic'] == prod_anthropic and
            has_embedded_keys() and
            is_production_build()
        )
        
        if embedded_correct:
            print("   ✅ Embedded keys module works correctly")
        else:
            print("   ❌ Embedded keys module failed")
            return False
        
        # Step 3: Test key resolver
        print("\n🔍 Testing key resolver...")
        from gsai.key_resolver import get_final_api_keys, get_key_status
        
        final_keys = get_final_api_keys()
        status = get_key_status()
        
        print(f"   Final keys: OpenAI={bool(final_keys['openai_key'])}, Anthropic={bool(final_keys['anthropic_key'])}")
        print(f"   Sources: OpenAI={final_keys['openai_source']}, Anthropic={final_keys['anthropic_source']}")
        print(f"   Has any keys: {final_keys['has_any']}")
        print(f"   Status has keys: {status['has_keys']}")
        
        resolver_correct = (
            final_keys['openai_key'] == prod_openai and
            final_keys['anthropic_key'] == prod_anthropic and
            final_keys['openai_source'] == 'embedded' and
            final_keys['anthropic_source'] == 'embedded' and
            final_keys['has_any'] and
            status['has_keys']
        )
        
        if resolver_correct:
            print("   ✅ Key resolver works correctly")
        else:
            print("   ❌ Key resolver failed")
            return False
        
        # Step 4: Test chat session key checking (without full chat system)
        print("\n🔍 Testing chat key validation...")
        
        # Simulate the key checking logic
        try:
            from gsai.key_resolver import get_key_status
            status = get_key_status()
            
            if status['has_keys']:
                available_keys = []
                if status['openai']['available']:
                    available_keys.append(f"OpenAI ({status['openai']['source']})")
                if status['anthropic']['available']:
                    available_keys.append(f"Anthropic ({status['anthropic']['source']})")
                
                print(f"   ✅ Chat would show: API keys ready: {', '.join(available_keys)}")
                chat_correct = True
            else:
                print("   ❌ Chat would show: No API keys available")
                chat_correct = False
                
        except Exception as e:
            print(f"   ❌ Chat validation failed: {e}")
            chat_correct = False
        
        # Clean up
        config_path.unlink()
        
        print("\n📊 PRODUCTION SIMULATION RESULTS:")
        print(f"   Embedded keys: {'✅' if embedded_correct else '❌'}")
        print(f"   Key resolver: {'✅' if resolver_correct else '❌'}")
        print(f"   Chat validation: {'✅' if chat_correct else '❌'}")
        
        return embedded_correct and resolver_correct and chat_correct
        
    except Exception as e:
        print(f"❌ Production simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_environment_variable_priority():
    """Test that environment variables override embedded keys."""
    try:
        print("\n🌍 TESTING ENVIRONMENT VARIABLE PRIORITY")
        print("=" * 50)
        
        # Create production config
        from gsai.crypto_utils import encrypt_api_key
        
        embedded_openai = "sk-embedded-key"
        env_openai = "sk-env-override-key"
        
        encrypted_embedded = encrypt_api_key(embedded_openai)
        
        config_content = f'''"""Environment priority test config"""
EMBEDDED_OPENAI_API_KEY = "{encrypted_embedded}"
EMBEDDED_ANTHROPIC_API_KEY = ""
BUILD_TYPE = "production"
BUILD_TIMESTAMP = "2025-06-19T22:00:00Z"
BUILD_COMMIT_SHA = "envtest123"
'''
        
        config_path = project_root / "gsai" / "build_config.py"
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        # Set environment variable
        os.environ['OPENAI_API_KEY'] = env_openai
        
        print(f"✅ Setup: embedded='{embedded_openai}', env='{env_openai}'")
        
        # Clear module cache to force fresh import
        modules_to_clear = [name for name in sys.modules.keys() if name.startswith('gsai')]
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]
        
        # Test key resolver
        from gsai.key_resolver import get_final_api_keys
        
        final_keys = get_final_api_keys()
        
        print(f"   Final OpenAI key: {final_keys['openai_key']}")
        print(f"   Source: {final_keys['openai_source']}")
        
        priority_correct = (
            final_keys['openai_key'] == env_openai and
            final_keys['openai_source'] == 'environment'
        )
        
        if priority_correct:
            print("   ✅ Environment variable correctly overrides embedded key")
        else:
            print("   ❌ Environment variable priority failed")
        
        # Clean up
        del os.environ['OPENAI_API_KEY']
        config_path.unlink()
        
        return priority_correct
        
    except Exception as e:
        print(f"❌ Environment priority test failed: {e}")
        return False


if __name__ == "__main__":
    print("🔍 COMPLETE SYSTEM TEST")
    print("=" * 60)
    
    test1 = test_production_simulation()
    test2 = test_environment_variable_priority()
    
    print("\n" + "=" * 60)
    if test1 and test2:
        print("🎉 COMPLETE SYSTEM WORKS!")
        print("✅ Production builds will have embedded encrypted keys")
        print("✅ Users will see 'API keys ready' instead of setup prompt")
        print("✅ Environment variables properly override embedded keys")
        print("✅ Key sources are correctly identified and displayed")
        print("\n🚀 READY FOR DEPLOYMENT!")
    else:
        print("❌ SYSTEM HAS ISSUES!")
        print("⚠️ Users will still see the API key setup prompt")
        
    sys.exit(0 if (test1 and test2) else 1)