#!/usr/bin/env python3
"""
Debug script to simulate production environment and test key loading.
"""

import os
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_production_build_config():
    """Create a production build config with encrypted keys."""
    try:
        from gsai.crypto_utils import encrypt_api_key
        
        # Mock production API keys
        openai_key = "sk-test-production-openai-key-123456789"
        anthropic_key = "anthropic-test-production-key-987654321"
        
        # Encrypt them
        encrypted_openai = encrypt_api_key(openai_key)
        encrypted_anthropic = encrypt_api_key(anthropic_key)
        
        # Create production build config
        build_config_content = f'''"""
Build-time configuration with embedded API keys.
This file is generated during build and should not be committed.
Keys are encrypted for security.
"""

# These are populated during GitHub Actions build with encrypted keys
EMBEDDED_OPENAI_API_KEY = "{encrypted_openai}"
EMBEDDED_ANTHROPIC_API_KEY = "{encrypted_anthropic}"

# Build metadata
BUILD_TYPE = "production"
BUILD_TIMESTAMP = "2025-06-19T21:35:00Z"
BUILD_COMMIT_SHA = "test123456"
'''
        
        # Write the production config
        build_config_path = project_root / "gsai" / "build_config.py"
        with open(build_config_path, 'w') as f:
            f.write(build_config_content)
        
        print("✅ Created production build_config.py with encrypted keys")
        print(f"   OpenAI: {openai_key} -> {encrypted_openai[:50]}...")
        print(f"   Anthropic: {anthropic_key} -> {encrypted_anthropic[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create production build config: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_loading():
    """Test loading the config as the application would."""
    try:
        print("\n🔄 Testing config loading...")
        
        # Import the config system
        from gsai.config import cli_settings
        
        print(f"OpenAI Key: {'Set' if cli_settings.OPENAI_API_KEY else 'Empty'}")
        print(f"Anthropic Key: {'Set' if cli_settings.ANTHROPIC_API_KEY else 'Empty'}")
        
        # Test the validation logic from chat.py
        has_openai = cli_settings.OPENAI_API_KEY and cli_settings.OPENAI_API_KEY.strip()
        has_anthropic = cli_settings.ANTHROPIC_API_KEY and cli_settings.ANTHROPIC_API_KEY.strip()
        
        print(f"Valid OpenAI: {bool(has_openai)}")
        print(f"Valid Anthropic: {bool(has_anthropic)}")
        print(f"Would show setup prompt: {not (has_openai or has_anthropic)}")
        
        # Show actual key values (first 20 chars)
        if cli_settings.OPENAI_API_KEY:
            print(f"OpenAI value: {cli_settings.OPENAI_API_KEY[:20]}...")
        if cli_settings.ANTHROPIC_API_KEY:
            print(f"Anthropic value: {cli_settings.ANTHROPIC_API_KEY[:20]}...")
        
        return has_openai or has_anthropic
        
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chat_logic():
    """Test the chat session initialization logic."""
    try:
        print("\n🔄 Testing chat session logic...")
        
        from gsai.config import cli_settings
        
        # Simulate the exact logic from chat.py
        has_openai = cli_settings.OPENAI_API_KEY and cli_settings.OPENAI_API_KEY.strip()
        has_anthropic = cli_settings.ANTHROPIC_API_KEY and cli_settings.ANTHROPIC_API_KEY.strip()
        
        if not has_openai and not has_anthropic:
            print("❌ Chat would show 'No API keys configured' error")
            
            # Check build detection logic
            try:
                from gsai.build_config import EMBEDDED_OPENAI_API_KEY, EMBEDDED_ANTHROPIC_API_KEY, BUILD_TYPE
                is_built_version = bool(EMBEDDED_OPENAI_API_KEY or EMBEDDED_ANTHROPIC_API_KEY) or BUILD_TYPE == "production"
                
                print(f"Build type detected: {BUILD_TYPE}")
                print(f"Has embedded keys: {bool(EMBEDDED_OPENAI_API_KEY or EMBEDDED_ANTHROPIC_API_KEY)}")
                print(f"Is production build: {is_built_version}")
                
                if is_built_version:
                    print("🔍 Would show 'Build configuration issue' message")
                else:
                    print("🔍 Would show 'Development environment' message")
                    
            except ImportError as e:
                print(f"❌ Failed to import build_config: {e}")
                
            return False
        else:
            print("✅ Chat would work immediately - no setup prompt")
            return True
            
    except Exception as e:
        print(f"❌ Chat logic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def cleanup():
    """Clean up test artifacts."""
    build_config_path = project_root / "gsai" / "build_config.py"
    if build_config_path.exists():
        build_config_path.unlink()
        print("🧹 Cleaned up test build_config.py")


if __name__ == "__main__":
    try:
        print("🔍 PRODUCTION ENVIRONMENT SIMULATION")
        print("=" * 50)
        
        # Step 1: Create production build config
        if not create_production_build_config():
            sys.exit(1)
        
        # Step 2: Test config loading
        config_works = test_config_loading()
        
        # Step 3: Test chat logic
        chat_works = test_chat_logic()
        
        print("\n" + "=" * 50)
        if config_works and chat_works:
            print("🎉 SUCCESS: Production environment would work!")
            print("✅ Keys are properly decrypted and available")
            print("✅ Chat would start immediately without setup prompt")
        else:
            print("❌ FAILED: Production environment has issues")
            print("⚠️ Users would still see the setup prompt")
            
        sys.exit(0 if (config_works and chat_works) else 1)
        
    finally:
        cleanup()