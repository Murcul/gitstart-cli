#!/usr/bin/env python3
"""Debug script to check API key configuration."""

import sys
import os
sys.path.insert(0, '.')

from gsai.config import cli_settings
try:
    from gsai.build_config import EMBEDDED_OPENAI_API_KEY, EMBEDDED_ANTHROPIC_API_KEY
except ImportError:
    EMBEDDED_OPENAI_API_KEY = ''
    EMBEDDED_ANTHROPIC_API_KEY = ''

def debug_api_keys():
    print("🔍 API Key Debug Information")
    print("=" * 50)
    
    print(f"📦 Embedded OpenAI Key: {'✓ Set' if EMBEDDED_OPENAI_API_KEY else '✗ Empty'}")
    print(f"📦 Embedded Anthropic Key: {'✓ Set' if EMBEDDED_ANTHROPIC_API_KEY else '✗ Empty'}")
    
    print(f"⚙️  Config OpenAI Key: {'✓ Set' if cli_settings.OPENAI_API_KEY else '✗ Empty'}")
    print(f"⚙️  Config Anthropic Key: {'✓ Set' if cli_settings.ANTHROPIC_API_KEY else '✗ Empty'}")
    
    print(f"🌍 ENV OpenAI Key: {'✓ Set' if os.getenv('OPENAI_API_KEY') else '✗ Empty'}")
    print(f"🌍 ENV Anthropic Key: {'✓ Set' if os.getenv('ANTHROPIC_API_KEY') else '✗ Empty'}")
    
    # Check what the validation would see
    has_openai = cli_settings.OPENAI_API_KEY and cli_settings.OPENAI_API_KEY.strip()
    has_anthropic = cli_settings.ANTHROPIC_API_KEY and cli_settings.ANTHROPIC_API_KEY.strip()
    
    print("\n🧪 Validation Results:")
    print(f"   OpenAI Valid: {'✓ Yes' if has_openai else '✗ No'}")
    print(f"   Anthropic Valid: {'✓ Yes' if has_anthropic else '✗ No'}")
    print(f"   Either Valid: {'✓ Yes' if (has_openai or has_anthropic) else '✗ No'}")
    
    if not (has_openai or has_anthropic):
        print("\n⚠️  This is why you're seeing the setup prompt!")
        print("\n💡 Solutions:")
        print("   1. Set environment variables:")
        print("      export OPENAI_API_KEY='your-key-here'")
        print("      export ANTHROPIC_API_KEY='your-key-here'")
        print("   2. Run: gsai configure")
        print("   3. Create embedded build with API keys")
    else:
        print("\n✅ API keys are properly configured!")

if __name__ == "__main__":
    debug_api_keys()