#!/bin/bash

# GitStart CoPilot CLI - Simplified Installer
# One-command installation script using uv tool install
# Usage: curl -sSL https://raw.githubusercontent.com/Murcul/gitstart-cli/main/install.sh | bash

set -e  # Exit on any error

# Colors for beautiful output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/Murcul/gitstart-cli"
ARCHIVE_URL="https://github.com/Murcul/gitstart-cli/archive/refs/heads/main.zip"
TEMP_DIR="/tmp/gsai-install-$$"
APP_NAME="gsai"
PYTHON_MIN_VERSION="3.10"

# Functions
print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║               GitStart CoPilot CLI Installer             ║"
    echo "║                   Made by GitStart AI 🤖                ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo -e "${WHITE}✨ One-command installation - no manual setup required!${NC}"
    echo ""
}

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Cleanup function
cleanup() {
    if [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
    fi
}

# Set trap for cleanup
trap cleanup EXIT

# Detect OS and architecture
detect_system() {
    print_step "Detecting system configuration..."
    
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)
    
    case $ARCH in
        x86_64|amd64)
            ARCH="x64"
            ;;
        arm64|aarch64)
            ARCH="arm64"
            ;;
        armv7l)
            ARCH="arm"
            ;;
        *)
            print_error "Unsupported architecture: $ARCH"
            exit 1
            ;;
    esac
    
    print_success "Detected: $OS-$ARCH"
}

# Check prerequisites
check_prerequisites() {
    print_step "Checking system prerequisites..."
    
    # Check for required commands
    local missing_commands=()
    
    for cmd in curl unzip python3; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_commands+=("$cmd")
        fi
    done
    
    # Install missing commands based on OS
    if [ ${#missing_commands[@]} -gt 0 ]; then
        print_warning "Missing commands: ${missing_commands[*]}"
        install_prerequisites "${missing_commands[@]}"
    fi
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        if ! python3 -c "import sys; exit(0 if sys.version_info >= tuple(map(int, '$PYTHON_MIN_VERSION'.split('.'))) else 1)" 2>/dev/null; then
            print_warning "Python $PYTHON_VERSION detected. Installing Python 3.10+..."
            install_python
        else
            print_success "Python $PYTHON_VERSION detected ✓"
        fi
    fi
}

# Install prerequisites based on OS
install_prerequisites() {
    local commands=("$@")
    
    case $OS in
        linux)
            # Detect Linux distribution
            if [ -f /etc/os-release ]; then
                . /etc/os-release
                DISTRO=$ID
            else
                DISTRO="unknown"
            fi
            
            case $DISTRO in
                ubuntu|debian)
                    print_info "Installing prerequisites with apt..."
                    sudo apt-get update -qq
                    for cmd in "${commands[@]}"; do
                        case $cmd in
                            curl) sudo apt-get install -y curl ;;
                            unzip) sudo apt-get install -y unzip ;;
                            python3) sudo apt-get install -y python3 python3-pip python3-venv ;;
                        esac
                    done
                    ;;
                centos|rhel|fedora)
                    print_info "Installing prerequisites with dnf/yum..."
                    if command -v dnf &> /dev/null; then
                        PKG_MANAGER="dnf"
                    else
                        PKG_MANAGER="yum"
                    fi
                    for cmd in "${commands[@]}"; do
                        case $cmd in
                            curl) sudo $PKG_MANAGER install -y curl ;;
                            unzip) sudo $PKG_MANAGER install -y unzip ;;
                            python3) sudo $PKG_MANAGER install -y python3 python3-pip ;;
                        esac
                    done
                    ;;
                arch|manjaro)
                    print_info "Installing prerequisites with pacman..."
                    for cmd in "${commands[@]}"; do
                        case $cmd in
                            curl) sudo pacman -S --noconfirm curl ;;
                            unzip) sudo pacman -S --noconfirm unzip ;;
                            python3) sudo pacman -S --noconfirm python python-pip ;;
                        esac
                    done
                    ;;
                alpine)
                    print_info "Installing prerequisites with apk..."
                    for cmd in "${commands[@]}"; do
                        case $cmd in
                            curl) sudo apk add curl ;;
                            unzip) sudo apk add unzip ;;
                            python3) sudo apk add python3 py3-pip ;;
                        esac
                    done
                    ;;
                *)
                    print_error "Unsupported Linux distribution: $DISTRO"
                    print_info "Please install manually: ${commands[*]}"
                    exit 1
                    ;;
            esac
            ;;
        darwin)
            print_info "Installing prerequisites with Homebrew..."
            if ! command -v brew &> /dev/null; then
                print_info "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            for cmd in "${commands[@]}"; do
                case $cmd in
                    python3) brew install python@3.10 ;;
                    *) brew install "$cmd" ;;
                esac
            done
            ;;
        *)
            print_error "Unsupported operating system: $OS"
            exit 1
            ;;
    esac
    
    print_success "Prerequisites installed ✓"
}

# Install Python if needed
install_python() {
    case $OS in
        linux)
            if [ -f /etc/os-release ]; then
                . /etc/os-release
                DISTRO=$ID
            fi
            
            case $DISTRO in
                ubuntu|debian)
                    sudo apt-get update -qq
                    sudo apt-get install -y software-properties-common
                    sudo add-apt-repository -y ppa:deadsnakes/ppa
                    sudo apt-get update -qq
                    sudo apt-get install -y python3.10 python3.10-venv python3.10-dev
                    # Create symlink if needed
                    if ! command -v python3 &> /dev/null; then
                        sudo ln -sf /usr/bin/python3.10 /usr/bin/python3
                    fi
                    ;;
                centos|rhel|fedora)
                    if command -v dnf &> /dev/null; then
                        sudo dnf install -y python3.10 python3.10-pip python3.10-devel
                    else
                        sudo yum install -y python3.10 python3.10-pip python3.10-devel
                    fi
                    ;;
                *)
                    print_warning "Please install Python 3.10+ manually for your distribution"
                    ;;
            esac
            ;;
        darwin)
            if command -v brew &> /dev/null; then
                brew install python@3.10
            else
                print_warning "Please install Python 3.10+ from python.org"
                exit 1
            fi
            ;;
    esac
}

# Install uv (Python package manager)
install_uv() {
    print_step "Installing uv package manager..."
    
    if command -v uv &> /dev/null; then
        print_success "uv already installed ✓"
        return
    fi
    
    # Install uv
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add to PATH for current session
    export PATH="$HOME/.local/bin:$PATH"
    
    # Verify installation
    if command -v uv &> /dev/null; then
        print_success "uv installed successfully ✓"
    else
        print_error "Failed to install uv"
        exit 1
    fi
}

# Download source code
download_source() {
    print_step "Downloading GitStart CoPilot CLI source code..."
    
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR"
    
    # Download archive
    if curl -L "$ARCHIVE_URL" -o source.zip; then
        print_success "Source code downloaded ✓"
    else
        print_error "Failed to download source code"
        exit 1
    fi
    
    # Extract archive
    if unzip -q source.zip; then
        print_success "Source code extracted ✓"
    else
        print_error "Failed to extract source code"
        exit 1
    fi
    
    # Find extracted directory
    EXTRACTED_DIR=$(find . -maxdepth 1 -type d -name "gitstart-cli-*" | head -1)
    if [ -n "$EXTRACTED_DIR" ]; then
        cd "$EXTRACTED_DIR"
        print_success "Entered source directory: $EXTRACTED_DIR"
    else
        print_error "Could not find extracted source directory"
        exit 1
    fi
}

# Install application using uv tool
install_application() {
    print_step "Installing GitStart CoPilot CLI..."
    
    # Install using uv tool
    if uv tool install .; then
        print_success "Installed via uv tool ✓"
    else
        print_error "Failed to install via uv tool"
        exit 1
    fi
}

# Configure PATH
configure_path() {
    print_step "Configuring PATH..."
    
    # uv tool installs to ~/.local/bin by default
    LOCAL_BIN="$HOME/.local/bin"
    
    # Check if already in PATH
    if echo "$PATH" | grep -q "$LOCAL_BIN"; then
        print_success "PATH already configured ✓"
        return
    fi
    
    # Add to shell profiles
    local shell_profiles=(
        "$HOME/.bashrc"
        "$HOME/.zshrc"
        "$HOME/.profile"
    )
    
    local path_line="export PATH=\"$LOCAL_BIN:\$PATH\""
    
    print_info "Adding to shell profiles..."
    for profile in "${shell_profiles[@]}"; do
        if [ -f "$profile" ]; then
            if ! grep -q "$LOCAL_BIN" "$profile"; then
                echo "" >> "$profile"
                echo "# GitStart CoPilot CLI" >> "$profile"
                echo "$path_line" >> "$profile"
                print_info "Added to $profile"
            fi
        fi
    done
    
    # Add to current session
    export PATH="$LOCAL_BIN:$PATH"
    
    print_success "PATH configured ✓"
}

# Configure API keys
configure_api_keys() {
    print_step "Setting up configuration..."
    
    # Create config directory
    mkdir -p "$HOME/.ai/gsai"
    
    # Create basic config file
    cat > "$HOME/.ai/gsai/.env" << 'EOF'
# GitStart CoPilot CLI Configuration
# Generated by installer

# API Keys (add your keys here)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Default Settings
APPROVAL_MODE=suggest
WEB_SEARCH_ENABLED=false
LOG_LEVEL=INFO

# Model Configuration
CODING_AGENT_MODEL_NAME=anthropic:claude-3-haiku-20240307
QA_AGENT_MODEL_NAME=openai:gpt-3.5-turbo
EOF
    
    chmod 600 "$HOME/.ai/gsai/.env"
    print_success "Configuration template created ✓"
}

# Test installation
test_installation() {
    print_step "Testing installation..."
    
    if command -v gsai &> /dev/null; then
        if gsai --version &> /dev/null; then
            print_success "Installation test passed ✓"
            return 0
        else
            print_warning "gsai command found but failed to run"
            return 1
        fi
    else
        print_warning "gsai command not found in PATH"
        print_info "You may need to restart your terminal or run: export PATH=\"$HOME/.local/bin:\$PATH\""
        return 1
    fi
}

# Show completion message
show_completion() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                 🎉 Installation Complete! 🎉             ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${WHITE}GitStart CoPilot CLI has been successfully installed!${NC}"
    echo ""
    echo -e "${CYAN}Quick Start:${NC}"
    echo -e "  ${YELLOW}1.${NC} Restart your terminal or run: ${WHITE}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
    echo -e "  ${YELLOW}2.${NC} Configure your API keys: ${WHITE}gsai configure${NC}"
    echo -e "  ${YELLOW}3.${NC} Start coding with AI: ${WHITE}gsai chat${NC}"
    echo ""
    echo -e "${CYAN}Commands:${NC}"
    echo -e "  ${WHITE}gsai --help${NC}        - Show help"
    echo -e "  ${WHITE}gsai configure${NC}     - Set up API keys"
    echo -e "  ${WHITE}gsai status${NC}        - Check configuration"
    echo -e "  ${WHITE}gsai chat${NC}          - Start AI coding session"
    echo ""
    echo -e "${CYAN}Configuration:${NC}"
    echo -e "  Config file: ${WHITE}$HOME/.ai/gsai/.env${NC}"
    echo -e "  Install location: ${WHITE}$HOME/.local/bin/gsai${NC}"
    echo ""
    echo -e "${BLUE}Get API keys:${NC}"
    echo -e "  OpenAI: ${WHITE}https://platform.openai.com/api-keys${NC}"
    echo -e "  Anthropic: ${WHITE}https://console.anthropic.com/${NC}"
    echo ""
    echo -e "${PURPLE}Need help? Check the documentation or visit:${NC}"
    echo -e "  ${WHITE}https://github.com/your-org/gitstart-cli${NC}"
    echo ""
}

# Main installation function
main() {
    print_banner
    
    # Installation steps
    detect_system
    check_prerequisites
    install_uv
    download_source
    install_application
    configure_path
    configure_api_keys
    
    # Test and complete
    if test_installation; then
        show_completion
    else
        show_completion
        echo -e "${YELLOW}Note: You may need to restart your terminal for the PATH changes to take effect.${NC}"
    fi
}

# Run main function
main "$@"