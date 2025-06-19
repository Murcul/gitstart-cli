#!/bin/bash

# GitStart CoPilot CLI - Universal Installer
# One-command installation script that handles everything
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
PYTHON_MIN_VERSION="3.10"  # Relaxed for wider compatibility

# Determine installation directory - default to system-wide
if [ -z "$INSTALL_DIR" ]; then
    # Try system-wide first (/usr/local/bin)
    if [ -w "/usr/local/bin" ] || [ "$(id -u)" = "0" ]; then
        INSTALL_DIR="/usr/local/bin"
        IS_SYSTEM_INSTALL=true
    elif command -v sudo >/dev/null 2>&1; then
        # Ask user preference if sudo is available
        echo "GitStart CoPilot CLI can be installed system-wide (/usr/local/bin) or user-only (~/.local/bin)"
        echo "System-wide installation makes 'gsai' available for all users"
        read -p "Install system-wide (requires sudo) [Y/n]? " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            INSTALL_DIR="/usr/local/bin"
            IS_SYSTEM_INSTALL=true
        else
            INSTALL_DIR="$HOME/.local/bin"
            IS_SYSTEM_INSTALL=false
        fi
    else
        # No sudo, fall back to user install
        INSTALL_DIR="$HOME/.local/bin"
        IS_SYSTEM_INSTALL=false
    fi
else
    # User specified INSTALL_DIR
    if [[ "$INSTALL_DIR" == "/usr/local/bin" ]] || [[ "$INSTALL_DIR" == "/usr/bin" ]]; then
        IS_SYSTEM_INSTALL=true
    else
        IS_SYSTEM_INSTALL=false
    fi
fi

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

# Build application
build_application() {
    print_step "Building GitStart CoPilot CLI..."
    
    # Install dependencies and build
    if uv sync; then
        print_success "Dependencies installed ✓"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
    
    # Create executable using PyInstaller
    print_info "Creating standalone executable..."
    
    # Create a simple build script
    cat > build_simple.py << 'EOF'
import subprocess
import sys
import os
from pathlib import Path

def build_executable():
    try:
        # Install PyInstaller
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        
        # Create spec file
        spec_content = '''
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path('.').resolve()))

a = Analysis(
    ['gsai/main.py'],
    pathex=[str(Path('.').resolve())],
    binaries=[],
    datas=[],
    hiddenimports=[
        'gsai',
        'gsai.main',
        'gsai.config',
        'gsai.chat',
        'pydantic_ai',
        'openai',
        'anthropic',
        'typer',
        'rich',
        'pydantic',
        'pydantic_settings',
        'loguru',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'tkinter',
        'pytest',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='gsai',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=True,
)
'''
        
        with open('gsai_simple.spec', 'w') as f:
            f.write(spec_content)
        
        # Build with PyInstaller
        subprocess.run([sys.executable, "-m", "PyInstaller", "gsai_simple.spec", "--clean", "--noconfirm"], check=True)
        
        return True
    except Exception as e:
        print(f"Build failed: {e}")
        return False

if __name__ == "__main__":
    if build_executable():
        print("Build successful!")
        sys.exit(0)
    else:
        print("Build failed!")
        sys.exit(1)
EOF
    
    # Try building with PyInstaller
    if uv run python build_simple.py; then
        if [ -f "dist/gsai" ]; then
            print_success "Executable built successfully ✓"
        else
            # Fallback: create a wrapper script
            print_warning "PyInstaller build failed, creating wrapper script..."
            create_wrapper_script
        fi
    else
        # Fallback: create a wrapper script
        print_warning "Build failed, creating wrapper script..."
        create_wrapper_script
    fi
}

# Create wrapper script as fallback
create_wrapper_script() {
    print_info "Creating wrapper script..."
    
    # Install globally using uv
    if uv tool install .; then
        print_success "Installed via uv tool ✓"
        return
    fi
    
    # Create manual wrapper script
    mkdir -p "$INSTALL_DIR"
    
    cat > "$INSTALL_DIR/gsai" << EOF
#!/bin/bash
# GitStart CoPilot CLI Wrapper Script
# Auto-generated by installer

SCRIPT_DIR="\$HOME/.gsai"
VENV_DIR="\$SCRIPT_DIR/venv"

# Create virtual environment if it doesn't exist
if [ ! -d "\$VENV_DIR" ]; then
    python3 -m venv "\$VENV_DIR"
    source "\$VENV_DIR/bin/activate"
    pip install -e "\$SCRIPT_DIR/source"
else
    source "\$VENV_DIR/bin/activate"
fi

# Run gsai
exec python -m gsai "\$@"
EOF
    
    chmod +x "$INSTALL_DIR/gsai"
    
    # Copy source to permanent location
    mkdir -p "$HOME/.gsai"
    cp -r . "$HOME/.gsai/source"
    
    print_success "Wrapper script created ✓"
}

# Install the application
install_application() {
    print_step "Installing GitStart CoPilot CLI..."
    
    # Create install directory (with sudo if needed for system install)
    if [ "$IS_SYSTEM_INSTALL" = true ] && [ "$(id -u)" != "0" ]; then
        print_info "Creating system directory (requires sudo)..."
        sudo mkdir -p "$INSTALL_DIR"
    else
        mkdir -p "$INSTALL_DIR"
    fi
    
    # Copy executable or ensure wrapper is in place
    if [ -f "dist/gsai" ]; then
        if [ "$IS_SYSTEM_INSTALL" = true ] && [ "$(id -u)" != "0" ]; then
            print_info "Installing system-wide (requires sudo)..."
            sudo cp "dist/gsai" "$INSTALL_DIR/gsai"
            sudo chmod +x "$INSTALL_DIR/gsai"
            print_success "Executable installed system-wide to $INSTALL_DIR/gsai ✓"
        else
            cp "dist/gsai" "$INSTALL_DIR/gsai"
            chmod +x "$INSTALL_DIR/gsai"
            print_success "Executable installed to $INSTALL_DIR/gsai ✓"
        fi
    elif [ -f "$INSTALL_DIR/gsai" ]; then
        print_success "Wrapper script already installed ✓"
    else
        print_error "No executable or wrapper script found"
        exit 1
    fi
}

# Configure PATH
configure_path() {
    print_step "Configuring PATH..."
    
    # Check if already in PATH
    if echo "$PATH" | grep -q "$INSTALL_DIR"; then
        print_success "PATH already configured ✓"
        return
    fi
    
    if [ "$IS_SYSTEM_INSTALL" = true ]; then
        # System install - /usr/local/bin should already be in PATH
        if [[ "$INSTALL_DIR" == "/usr/local/bin" ]]; then
            print_success "System PATH configured (using /usr/local/bin) ✓"
            # Add to current session just in case
            export PATH="$INSTALL_DIR:$PATH"
            return
        elif [[ "$INSTALL_DIR" == "/usr/bin" ]]; then
            print_success "System PATH configured (using /usr/bin) ✓"
            export PATH="$INSTALL_DIR:$PATH"
            return
        fi
    fi
    
    # User install or custom location - add to shell profiles
    local shell_profiles=(
        "$HOME/.bashrc"
        "$HOME/.zshrc"
        "$HOME/.profile"
    )
    
    local path_line="export PATH=\"$INSTALL_DIR:\$PATH\""
    
    print_info "Adding to shell profiles..."
    for profile in "${shell_profiles[@]}"; do
        if [ -f "$profile" ]; then
            if ! grep -q "$INSTALL_DIR" "$profile"; then
                echo "" >> "$profile"
                echo "# GitStart CoPilot CLI" >> "$profile"
                echo "$path_line" >> "$profile"
                print_info "Added to $profile"
            fi
        fi
    done
    
    # Add to current session
    export PATH="$INSTALL_DIR:$PATH"
    
    if [ "$IS_SYSTEM_INSTALL" = true ]; then
        print_success "System PATH configured ✓"
    else
        print_success "User PATH configured ✓"
    fi
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
        print_info "You may need to restart your terminal or run: export PATH=\"$INSTALL_DIR:\$PATH\""
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
    echo -e "  ${YELLOW}1.${NC} Restart your terminal or run: ${WHITE}export PATH=\"$INSTALL_DIR:\$PATH\"${NC}"
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
    echo -e "  Install location: ${WHITE}$INSTALL_DIR/gsai${NC}"
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
    build_application
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
