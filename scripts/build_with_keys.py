#!/usr/bin/env python3
"""
Build script to embed encrypted API keys during GitHub Actions build.
"""

import os
import sys
import datetime
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gsai.crypto_utils import encrypt_api_key


def embed_keys():
    """Embed encrypted API keys into build_config.py during CI/CD."""
    
    # Get API keys from environment (GitHub Secrets)
    openai_key = os.getenv('OPENAI_API_KEY', '')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
    
    if not openai_key and not anthropic_key:
        print("⚠️ Warning: No API keys found in environment variables")
        print("   Make sure OPENAI_API_KEY and/or ANTHROPIC_API_KEY are set in GitHub Secrets")
        return False
    
    # Encrypt the keys
    encrypted_openai = encrypt_api_key(openai_key) if openai_key else ""
    encrypted_anthropic = encrypt_api_key(anthropic_key) if anthropic_key else ""
    
    # Get build metadata
    build_timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    commit_sha = os.getenv('GITHUB_SHA', 'unknown')
    
    # Generate the build_config.py content
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
BUILD_TIMESTAMP = "{build_timestamp}"
BUILD_COMMIT_SHA = "{commit_sha}"
'''
    
    # Write to build_config.py
    build_config_path = project_root / "gsai" / "build_config.py"
    
    with open(build_config_path, 'w') as f:
        f.write(build_config_content)
    
    print("✅ Successfully embedded encrypted API keys into build_config.py")
    print(f"   - OpenAI Key: {'✓ Embedded' if encrypted_openai else '✗ Not provided'}")
    print(f"   - Anthropic Key: {'✓ Embedded' if encrypted_anthropic else '✗ Not provided'}")
    print(f"   - Build Timestamp: {build_timestamp}")
    print(f"   - Commit SHA: {commit_sha}")
    
    return True


if __name__ == "__main__":
    success = embed_keys()
    sys.exit(0 if success else 1)