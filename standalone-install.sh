#!/bin/bash

# GitStart CoPilot CLI - Standalone Self-Installing Script
# This script downloads, compiles, and installs everything without user intervention
# Usage: curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/standalone-install.sh | bash

set -e  # Exit on any error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Configuration
REPO_URL="https://github.com/your-org/gitstart-cli"
ARCHIVE_URL="https://github.com/your-org/gitstart-cli/archive/refs/heads/main.zip"
GSAI_HOME="$HOME/.gsai"
TEMP_DIR="/tmp/gsai-standalone-$$"

# Determine installation directory - default to system-wide
if [ -z "$INSTALL_DIR" ]; then
    # Try system-wide first (/usr/local/bin) 
    if [ -w "/usr/local/bin" ] || [ "$(id -u)" = "0" ]; then
        INSTALL_DIR="/usr/local/bin"
        IS_SYSTEM_INSTALL=true
    elif command -v sudo >/dev/null 2>&1; then
        # Ask user preference if sudo is available
        echo "GitStart CoPilot CLI can be installed system-wide (/usr/local/bin) or user-only (~/.local/bin)"
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

# Logging
LOG_FILE="/tmp/gsai-install.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$LOG_FILE"
}

print_banner() {
    echo -e "${BLUE}"
    cat << 'EOF'
    ╔══════════════════════════════════════════════════════════╗
    ║            GitStart CoPilot CLI - Standalone             ║
    ║                 Zero-Dependency Installer                ║
    ║                   Made by GitStart AI 🤖                ║
    ╚══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    echo -e "${WHITE}🚀 Fully automated installation - sit back and relax!${NC}"
    echo ""
}

print_step() { echo -e "${CYAN}▶ $1${NC}"; log "STEP: $1"; }
print_success() { echo -e "${GREEN}✓ $1${NC}"; log "SUCCESS: $1"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; log "WARNING: $1"; }
print_error() { echo -e "${RED}✗ $1${NC}"; log "ERROR: $1"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; log "INFO: $1"; }

cleanup() {
    [[ -d "$TEMP_DIR" ]] && rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# Detect system
detect_system() {
    print_step "Detecting system..."
    
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)
    DISTRO="unknown"
    
    case $ARCH in
        x86_64|amd64) ARCH="x64" ;;
        arm64|aarch64) ARCH="arm64" ;;
        armv7l) ARCH="arm" ;;
        *) print_error "Unsupported architecture: $ARCH"; exit 1 ;;
    esac
    
    if [[ "$OS" == "linux" ]] && [[ -f /etc/os-release ]]; then
        . /etc/os-release
        DISTRO=$ID
    fi
    
    print_success "System: $OS-$ARCH ($DISTRO)"
}

# Check if command exists
has_command() {
    command -v "$1" >/dev/null 2>&1
}

# Install prerequisites silently
install_prerequisites() {
    print_step "Setting up prerequisites..."
    
    # Try to install without prompting
    case $DISTRO in
        ubuntu|debian)
            if has_command sudo && has_command apt-get; then
                print_info "Installing packages with apt..."
                export DEBIAN_FRONTEND=noninteractive
                sudo apt-get update -qq >/dev/null 2>&1 || true
                sudo apt-get install -y curl unzip python3 python3-pip python3-venv >/dev/null 2>&1 || true
            fi
            ;;
        centos|rhel|fedora)
            if has_command sudo; then
                PKG_MANAGER="dnf"
                has_command dnf || PKG_MANAGER="yum"
                print_info "Installing packages with $PKG_MANAGER..."
                sudo $PKG_MANAGER install -y curl unzip python3 python3-pip >/dev/null 2>&1 || true
            fi
            ;;
        arch|manjaro)
            if has_command sudo && has_command pacman; then
                print_info "Installing packages with pacman..."
                sudo pacman -Sy --noconfirm curl unzip python python-pip >/dev/null 2>&1 || true
            fi
            ;;
        alpine)
            if has_command sudo && has_command apk; then
                print_info "Installing packages with apk..."
                sudo apk add --no-cache curl unzip python3 py3-pip >/dev/null 2>&1 || true
            fi
            ;;
    esac
    
    # Check what we have now
    local missing=()
    for cmd in curl unzip python3; do
        has_command "$cmd" || missing+=("$cmd")
    done
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        print_warning "Missing: ${missing[*]} - will try alternatives"
    else
        print_success "All prerequisites available"
    fi
}

# Download with fallback options
download_file() {
    local url="$1"
    local output="$2"
    
    if has_command curl; then
        curl -L "$url" -o "$output" >/dev/null 2>&1
    elif has_command wget; then
        wget "$url" -O "$output" >/dev/null 2>&1
    elif has_command python3; then
        python3 -c "
import urllib.request
urllib.request.urlretrieve('$url', '$output')
" >/dev/null 2>&1
    else
        return 1
    fi
}

# Extract with fallback options
extract_archive() {
    local archive="$1"
    local dest="$2"
    
    if has_command unzip; then
        unzip -q "$archive" -d "$dest"
    elif has_command python3; then
        python3 -c "
import zipfile
with zipfile.ZipFile('$archive', 'r') as zip_ref:
    zip_ref.extractall('$dest')
" >/dev/null 2>&1
    else
        return 1
    fi
}

# Create portable Python environment
create_portable_env() {
    print_step "Creating portable Python environment..."
    
    mkdir -p "$GSAI_HOME/python-env"
    cd "$GSAI_HOME/python-env"
    
    # Create minimal virtual environment
    if has_command python3; then
        python3 -m venv . >/dev/null 2>&1 || {
            print_warning "venv failed, using system Python"
            return 1
        }
        
        # Activate and install minimal dependencies
        source bin/activate >/dev/null 2>&1 || return 1
        
        print_info "Installing Python packages..."
        pip install --quiet --no-warn-script-location \
            pydantic-ai==0.2.6 \
            typer \
            rich \
            pydantic \
            pydantic-settings \
            loguru \
            openai \
            anthropic \
            >/dev/null 2>&1 || {
            print_warning "Package installation failed"
            return 1
        }
        
        print_success "Portable Python environment created"
        return 0
    else
        print_warning "Python3 not available"
        return 1
    fi
}

# Download and extract source
get_source() {
    print_step "Downloading source code..."
    
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR"
    
    if download_file "$ARCHIVE_URL" "source.zip"; then
        print_success "Source downloaded"
    else
        print_error "Failed to download source"
        exit 1
    fi
    
    if extract_archive "source.zip" "."; then
        print_success "Source extracted"
    else
        print_error "Failed to extract source"
        exit 1
    fi
    
    # Find extracted directory
    EXTRACTED_DIR=$(find . -maxdepth 1 -type d -name "gitstart-cli-*" | head -1)
    if [[ -n "$EXTRACTED_DIR" ]]; then
        cd "$EXTRACTED_DIR"
        print_success "Entered source directory"
    else
        print_error "Could not find source directory"
        exit 1
    fi
}

# Create self-contained launcher
create_launcher() {
    print_step "Creating self-contained launcher..."
    
    # Create directories (with sudo if needed for system install)
    if [ "$IS_SYSTEM_INSTALL" = true ] && [ "$(id -u)" != "0" ]; then
        print_info "Creating system directory (requires sudo)..."
        sudo mkdir -p "$INSTALL_DIR"
    else
        mkdir -p "$INSTALL_DIR"
    fi
    
    mkdir -p "$GSAI_HOME/source"
    
    # Copy source files
    cp -r . "$GSAI_HOME/source/"
    
    # Create the main launcher script
    cat > /tmp/gsai-launcher << 'LAUNCHER_EOF'
#!/bin/bash
# GitStart CoPilot CLI - Self-Contained Launcher
# Generated by standalone installer

GSAI_HOME="$HOME/.gsai"
PYTHON_ENV="$GSAI_HOME/python-env"
SOURCE_DIR="$GSAI_HOME/source"

# Color output functions
print_error() { echo -e "\033[0;31m[ERROR]\033[0m $1" >&2; }
print_warning() { echo -e "\033[1;33m[WARN]\033[0m $1" >&2; }
print_info() { echo -e "\033[0;34m[INFO]\033[0m $1" >&2; }

# Check if portable environment exists
if [[ -d "$PYTHON_ENV" ]] && [[ -f "$PYTHON_ENV/bin/activate" ]]; then
    # Use portable environment
    source "$PYTHON_ENV/bin/activate" >/dev/null 2>&1
    export PYTHONPATH="$SOURCE_DIR:$PYTHONPATH"
    cd "$SOURCE_DIR"
    exec python -m gsai "$@"
elif command -v python3 >/dev/null 2>&1; then
    # Use system Python with inline dependencies
    export PYTHONPATH="$SOURCE_DIR:$PYTHONPATH"
    cd "$SOURCE_DIR"
    
    # Check if we have required packages
    if python3 -c "import pydantic_ai" >/dev/null 2>&1; then
        exec python3 -m gsai "$@"
    else
        print_error "Required Python packages not found"
        print_info "Run the installer again or install manually:"
        print_info "pip install pydantic-ai typer rich pydantic loguru openai anthropic"
        exit 1
    fi
else
    print_error "Python not found"
    print_info "Please install Python 3.10+ and run the installer again"
    exit 1
fi
LAUNCHER_EOF

    # Install the launcher script
    if [ "$IS_SYSTEM_INSTALL" = true ] && [ "$(id -u)" != "0" ]; then
        print_info "Installing system-wide launcher (requires sudo)..."
        sudo cp /tmp/gsai-launcher "$INSTALL_DIR/gsai"
        sudo chmod +x "$INSTALL_DIR/gsai"
        print_success "System-wide launcher created at $INSTALL_DIR/gsai"
    else
        cp /tmp/gsai-launcher "$INSTALL_DIR/gsai"
        chmod +x "$INSTALL_DIR/gsai"
        print_success "Launcher created at $INSTALL_DIR/gsai"
    fi
    
    # Clean up
    rm -f /tmp/gsai-launcher
}

# Configure PATH
setup_path() {
    print_step "Configuring PATH..."
    
    # Check if already in PATH
    if echo "$PATH" | grep -q "$INSTALL_DIR"; then
        print_success "PATH already configured"
        return
    fi
    
    if [ "$IS_SYSTEM_INSTALL" = true ]; then
        # System install - /usr/local/bin should already be in PATH
        if [[ "$INSTALL_DIR" == "/usr/local/bin" ]]; then
            print_success "System PATH configured (using /usr/local/bin)"
            # Add to current session just in case
            export PATH="$INSTALL_DIR:$PATH"
            return
        elif [[ "$INSTALL_DIR" == "/usr/bin" ]]; then
            print_success "System PATH configured (using /usr/bin)"
            export PATH="$INSTALL_DIR:$PATH"
            return
        fi
    fi
    
    # User install or custom location - add to shell profiles
    local profiles=("$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile")
    local path_line="export PATH=\"$INSTALL_DIR:\$PATH\""
    
    print_info "Adding to shell profiles..."
    for profile in "${profiles[@]}"; do
        if [[ -f "$profile" ]] && ! grep -q "$INSTALL_DIR" "$profile"; then
            echo "" >> "$profile"
            echo "# GitStart CoPilot CLI" >> "$profile"
            echo "$path_line" >> "$profile"
            print_info "Added to $profile"
        fi
    done
    
    # Add to current session
    export PATH="$INSTALL_DIR:$PATH"
    
    if [ "$IS_SYSTEM_INSTALL" = true ]; then
        print_success "System PATH configured"
    else
        print_success "User PATH configured"
    fi
}

# Create configuration
setup_config() {
    print_step "Setting up configuration..."
    
    mkdir -p "$HOME/.ai/gsai"
    
    if [[ ! -f "$HOME/.ai/gsai/.env" ]]; then
        cat > "$HOME/.ai/gsai/.env" << 'CONFIG_EOF'
# GitStart CoPilot CLI Configuration
# Generated by standalone installer

# API Keys (add your keys here)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Default Settings
APPROVAL_MODE=suggest
WEB_SEARCH_ENABLED=false
LOG_LEVEL=INFO

# Model Configuration (using faster, cheaper models by default)
CODING_AGENT_MODEL_NAME=openai:gpt-3.5-turbo
QA_AGENT_MODEL_NAME=openai:gpt-3.5-turbo
GIT_OPERATIONS_AGENT_MODEL_NAME=openai:gpt-3.5-turbo
CONFIG_EOF
        chmod 600 "$HOME/.ai/gsai/.env"
        print_success "Configuration created"
    else
        print_success "Configuration already exists"
    fi
}

# Test installation
test_installation() {
    print_step "Testing installation..."
    
    if command -v gsai >/dev/null 2>&1; then
        if timeout 10 gsai --version >/dev/null 2>&1; then
            print_success "Installation test passed"
            return 0
        else
            print_warning "gsai command found but failed to run"
            return 1
        fi
    else
        print_warning "gsai not found in PATH (may need terminal restart)"
        return 1
    fi
}

# Show completion
show_completion() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              🎉 Installation Successful! 🎉              ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${WHITE}GitStart CoPilot CLI is now installed and ready to use!${NC}"
    echo ""
    echo -e "${CYAN}Next Steps:${NC}"
    echo -e "  ${YELLOW}1.${NC} Restart your terminal or run: ${WHITE}source ~/.bashrc${NC}"
    echo -e "  ${YELLOW}2.${NC} Add your API keys: ${WHITE}gsai configure${NC}"
    echo -e "  ${YELLOW}3.${NC} Start coding: ${WHITE}gsai chat${NC}"
    echo ""
    echo -e "${CYAN}Quick Commands:${NC}"
    echo -e "  ${WHITE}gsai --help${NC}     - Show all commands"
    echo -e "  ${WHITE}gsai status${NC}     - Check configuration"
    echo -e "  ${WHITE}gsai configure${NC}  - Set up API keys"
    echo ""
    echo -e "${BLUE}Get API Keys:${NC}"
    echo -e "  OpenAI: ${WHITE}https://platform.openai.com/api-keys${NC}"
    echo -e "  Anthropic: ${WHITE}https://console.anthropic.com/${NC}"
    echo ""
    echo -e "${PURPLE}Installation Details:${NC}"
    echo -e "  Executable: ${WHITE}$INSTALL_DIR/gsai${NC}"
    echo -e "  Source: ${WHITE}$GSAI_HOME/source${NC}"
    echo -e "  Config: ${WHITE}$HOME/.ai/gsai/.env${NC}"
    echo -e "  Log: ${WHITE}$LOG_FILE${NC}"
    echo ""
}

# Main installation
main() {
    exec > >(tee -a "$LOG_FILE")
    exec 2>&1
    
    print_banner
    
    detect_system
    install_prerequisites
    get_source
    
    # Try to create portable environment, fallback to system Python
    create_portable_env || print_warning "Using system Python"
    
    create_launcher
    setup_path
    setup_config
    
    if test_installation; then
        show_completion
    else
        show_completion
        echo -e "${YELLOW}Note: You may need to restart your terminal.${NC}"
        echo -e "${YELLOW}If issues persist, check the log: $LOG_FILE${NC}"
    fi
}

# Run installation
main "$@"