#!/bin/bash

# GitStart CoPilot CLI - One-Click Installer
# This script installs GitStart CoPilot CLI with embedded API keys

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="$HOME/.local/bin"
GSAI_DIR="$HOME/.ai/gsai"
BINARY_NAME="gsai"

# Functions
print_banner() {
    echo -e "${BLUE}"
    echo "=============================================="
    echo "    GitStart CoPilot CLI Installer"
    echo "    Made by GitStart AI 🤖"
    echo "=============================================="
    echo -e "${NC}"
}

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Python 3.12+
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed."
        print_error "Please install Python 3.12+ from https://www.python.org/downloads/"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)"; then
        print_error "Python 3.12+ is required. Found Python $python_version"
        print_error ""
        print_error "Please install Python 3.12+ using one of these methods:"
        print_error "  • Ubuntu/Debian: sudo apt update && sudo apt install python3.12"
        print_error "  • macOS: brew install python@3.12"
        print_error "  • From source: https://www.python.org/downloads/"
        print_error ""
        print_error "After installation, you may need to use 'python3.12' instead of 'python3'"
        
        # Check if python3.12 is available
        if command -v python3.12 &> /dev/null; then
            print_status "Found python3.12! You can modify this script to use python3.12"
            print_status "Or create an alias: alias python3=python3.12"
        fi
        
        exit 1
    fi
    
    print_status "Python $python_version detected ✓"
    
    # Check uv
    if ! command -v uv &> /dev/null; then
        print_status "Installing uv package manager..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
        source "$HOME/.bashrc" 2>/dev/null || true
        source "$HOME/.zshrc" 2>/dev/null || true
        
        if ! command -v uv &> /dev/null; then
            print_error "Failed to install uv. Please install manually: https://docs.astral.sh/uv/"
            exit 1
        fi
    fi
    
    print_status "uv package manager detected ✓"
    
    # Check git
    if ! command -v git &> /dev/null; then
        print_warning "Git is recommended for repository operations but not required."
    else
        print_status "Git detected ✓"
    fi
}

get_api_keys() {
    print_status "API Key Configuration"
    echo "GitStart CoPilot requires at least one API key to function."
    echo "You can skip this step and configure later with 'gsai configure'"
    echo ""
    
    # Get OpenAI API Key
    echo -n "Enter your OpenAI API Key (or press Enter to skip): "
    read -s OPENAI_KEY
    echo ""
    
    # Get Anthropic API Key
    echo -n "Enter your Anthropic API Key (or press Enter to skip): "
    read -s ANTHROPIC_KEY
    echo ""
    
    if [[ -z "$OPENAI_KEY" && -z "$ANTHROPIC_KEY" ]]; then
        print_warning "No API keys provided. You'll need to configure them later."
        return 1
    fi
    
    return 0
}

install_dependencies() {
    print_status "Installing dependencies..."
    
    # Sync dependencies
    uv sync --dev
    
    if [ $? -ne 0 ]; then
        print_error "Failed to install dependencies"
        exit 1
    fi
    
    print_status "Dependencies installed ✓"
}

install_gsai() {
    print_status "Installing GitStart CoPilot CLI..."
    
    # Create install directory
    mkdir -p "$INSTALL_DIR"
    
    # Install using uv tool
    if uv tool install . --force; then
        print_status "GitStart CoPilot CLI installed successfully ✓"
        
        # Add to PATH if not already there
        if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
            echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$HOME/.bashrc"
            echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$HOME/.zshrc" 2>/dev/null || true
            export PATH="$INSTALL_DIR:$PATH"
            print_status "Added $INSTALL_DIR to PATH"
        fi
        
        return 0
    else
        print_error "Failed to install GitStart CoPilot CLI"
        return 1
    fi
}

configure_api_keys() {
    if [[ -n "$OPENAI_KEY" || -n "$ANTHROPIC_KEY" ]]; then
        print_status "Configuring API keys..."
        
        # Create gsai config directory
        mkdir -p "$GSAI_DIR"
        
        # Create .env file
        cat > "$GSAI_DIR/.env" << EOF
# GitStart CoPilot CLI Configuration
# Generated by installer on $(date)

EOF
        
        if [[ -n "$OPENAI_KEY" ]]; then
            echo "OPENAI_API_KEY=$OPENAI_KEY" >> "$GSAI_DIR/.env"
            print_status "OpenAI API key configured ✓"
        fi
        
        if [[ -n "$ANTHROPIC_KEY" ]]; then
            echo "ANTHROPIC_API_KEY=$ANTHROPIC_KEY" >> "$GSAI_DIR/.env"
            print_status "Anthropic API key configured ✓"
        fi
        
        # Set secure permissions
        chmod 600 "$GSAI_DIR/.env"
        
        # Add default configuration
        cat >> "$GSAI_DIR/.env" << EOF

# Default Configuration
APPROVAL_MODE=suggest
WEB_SEARCH_ENABLED=false
LOG_LEVEL=INFO
EOF
        
        print_status "Configuration saved to $GSAI_DIR/.env"
    fi
}

test_installation() {
    print_status "Testing installation..."
    
    # Test if gsai is available
    if command -v gsai &> /dev/null; then
        print_status "Testing gsai command..."
        if gsai --help > /dev/null 2>&1; then
            print_status "Installation test passed ✓"
            return 0
        else
            print_error "gsai command failed"
            return 1
        fi
    else
        print_error "gsai command not found in PATH"
        print_warning "You may need to restart your terminal or run: export PATH=\"$INSTALL_DIR:\$PATH\""
        return 1
    fi
}

show_completion_message() {
    print_status "Installation completed successfully! 🎉"
    echo ""
    echo -e "${GREEN}GitStart CoPilot CLI is now installed and ready to use!${NC}"
    echo ""
    echo "Quick Start:"
    echo "  1. Open a new terminal (or run: source ~/.bashrc)"
    echo "  2. Navigate to your project directory"
    echo "  3. Run: gsai chat"
    echo ""
    echo "Useful Commands:"
    echo "  gsai --help          - Show help"
    echo "  gsai version         - Show version"
    echo "  gsai status          - Check configuration"
    echo "  gsai configure       - Configure settings"
    echo "  gsai chat            - Start AI coding session"
    echo ""
    echo "Configuration:"
    echo "  Config file: $GSAI_DIR/.env"
    echo "  Logs: Use 'gsai status' to check configuration"
    echo ""
    echo "Need help? Check the README.md file or visit the documentation."
}

cleanup() {
    print_status "Cleaning up temporary files..."
    # Remove any temporary files if needed
}

main() {
    print_banner
    
    # Check if we're in the right directory
    if [[ ! -f "pyproject.toml" ]] || [[ ! -f "gsai/main.py" ]]; then
        print_error "This script must be run from the GitStart CoPilot CLI directory"
        print_error "Please cd to the project directory and run: ./install.sh"
        exit 1
    fi
    
    # Trap to cleanup on exit
    trap cleanup EXIT
    
    # Installation steps
    check_prerequisites
    get_api_keys
    install_dependencies
    
    if install_gsai; then
        configure_api_keys
        if test_installation; then
            show_completion_message
        else
            print_warning "Installation completed but testing failed."
            print_warning "Try running 'gsai --help' in a new terminal."
        fi
    else
        print_error "Installation failed"
        exit 1
    fi
}

# Run main function
main "$@"