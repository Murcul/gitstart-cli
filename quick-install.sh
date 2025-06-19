#!/bin/bash
# GitStart CoPilot CLI - Quick One-Liner Installer
# Usage: curl -sSL https://raw.githubusercontent.com/your-repo/gitstart-cli/master/quick-install.sh | bash

set -e

REPO_URL="https://github.com/gitstart/gitstart-cli"  # Update with actual repo URL
TEMP_DIR=$(mktemp -d)
INSTALL_DIR="$HOME/.local/bin"

echo "🤖 GitStart CoPilot CLI Quick Installer"
echo "========================================"

# Check if running from existing directory
if [[ -f "pyproject.toml" && -f "gsai/main.py" ]]; then
    echo "✓ Running from existing GitStart CLI directory"
    WORK_DIR=$(pwd)
else
    echo "📥 Downloading GitStart CoPilot CLI..."
    
    # Check if git is available
    if command -v git &> /dev/null; then
        git clone "$REPO_URL" "$TEMP_DIR/gitstart-cli"
        WORK_DIR="$TEMP_DIR/gitstart-cli"
    else
        echo "❌ Git is required for this installer"
        echo "Please install git or download the repository manually"
        exit 1
    fi
fi

cd "$WORK_DIR"

# Run the full installer
echo "🚀 Starting installation..."
./install.sh

# Cleanup
if [[ "$WORK_DIR" == "$TEMP_DIR"* ]]; then
    rm -rf "$TEMP_DIR"
fi

echo "✅ Installation complete!"
echo "💡 Run 'gsai chat' in your project directory to get started"