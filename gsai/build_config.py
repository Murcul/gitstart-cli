"""
Build-time configuration with embedded API keys.
This file is generated during build and should not be committed.
Keys are encrypted for security.
"""

# These will be populated during GitHub Actions build with encrypted keys
EMBEDDED_OPENAI_API_KEY = ""
EMBEDDED_ANTHROPIC_API_KEY = ""

# Build metadata
BUILD_TYPE = "development"  # Will be set to "production" during GitHub Actions
BUILD_TIMESTAMP = ""
BUILD_COMMIT_SHA = ""
