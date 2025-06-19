#!/bin/bash

# Local build script for testing PyInstaller configuration
# This script builds the executable locally for testing

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Clean previous builds
print_status "Cleaning previous builds..."
rm -rf dist/ build/ gsai/build_config.py

# Create dummy build config for testing
print_status "Creating test build config..."
cat > gsai/build_config.py << 'EOF'
"""
Build-time configuration with embedded API keys.
This file is generated during build and should not be committed.
"""

EMBEDDED_OPENAI_API_KEY = ""
EMBEDDED_ANTHROPIC_API_KEY = ""
EOF

# Backup original config
print_status "Backing up original config..."
cp gsai/config.py gsai/config.py.bak

# Modify config for build
print_status "Modifying config for build..."
cat > temp_config.py << 'EOF'
try:
    from gsai.build_config import EMBEDDED_OPENAI_API_KEY, EMBEDDED_ANTHROPIC_API_KEY
except ImportError:
    EMBEDDED_OPENAI_API_KEY = ''
    EMBEDDED_ANTHROPIC_API_KEY = ''

EOF
cat gsai/config.py >> temp_config.py

# Replace the API key fields
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' 's/OPENAI_API_KEY: str = Field(default="", description="OpenAI API Key")/OPENAI_API_KEY: str = Field(default=EMBEDDED_OPENAI_API_KEY or "", description="OpenAI API Key")/g' temp_config.py
    sed -i '' 's/ANTHROPIC_API_KEY: str = Field(default="", description="Anthropic API Key")/ANTHROPIC_API_KEY: str = Field(default=EMBEDDED_ANTHROPIC_API_KEY or "", description="Anthropic API Key")/g' temp_config.py
else
    # Linux
    sed -i 's/OPENAI_API_KEY: str = Field(default="", description="OpenAI API Key")/OPENAI_API_KEY: str = Field(default=EMBEDDED_OPENAI_API_KEY or "", description="OpenAI API Key")/g' temp_config.py
    sed -i 's/ANTHROPIC_API_KEY: str = Field(default="", description="Anthropic API Key")/ANTHROPIC_API_KEY: str = Field(default=EMBEDDED_ANTHROPIC_API_KEY or "", description="Anthropic API Key")/g' temp_config.py
fi

mv temp_config.py gsai/config.py

# Install PyInstaller if not already installed
print_status "Installing PyInstaller..."
uv add --dev pyinstaller

# Build with PyInstaller
print_status "Building executable with PyInstaller..."
uv run pyinstaller gsai.spec --clean --noconfirm

# Check if build was successful
if [ -f "dist/gsai" ]; then
    print_status "✅ Build successful!"
    
    # Make executable
    chmod +x dist/gsai
    
    # Show file info
    ls -la dist/gsai
    
    # Test basic functionality
    print_status "Testing executable..."
    if ./dist/gsai --version 2>/dev/null; then
        print_status "✅ Version check passed"
    else
        print_warning "Version check failed (may be expected without API keys)"
    fi
    
    if ./dist/gsai --help >/dev/null 2>&1; then
        print_status "✅ Help command works"
    else
        print_warning "Help command failed"
    fi
    
    print_status "Build completed successfully!"
    print_status "Executable location: $(pwd)/dist/gsai"
    
else
    print_error "❌ Build failed - executable not found"
    echo "Build output:"
    ls -la dist/ 2>/dev/null || echo "No dist directory found"
    exit 1
fi

# Cleanup
print_status "Restoring original files..."
if [ -f gsai/config.py.bak ]; then
    mv gsai/config.py.bak gsai/config.py
fi
rm -f gsai/build_config.py

print_status "Local build complete!"
echo ""
echo "To test the executable:"
echo "  ./dist/gsai --help"
echo "  ./dist/gsai version"
echo "  ./dist/gsai status"