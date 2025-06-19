# One-Line Installer Guide

Complete guide to using the automated installers for GitStart CoPilot CLI.

## 🚀 TL;DR - One Command Installation

### Linux/macOS
```bash
# Full installer (recommended)
curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.sh | bash

# Standalone installer (zero dependencies)
curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/standalone-install.sh | bash
```

### Windows
```powershell
# PowerShell installer
iwr -useb https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.ps1 | iex
```

**That's it!** No manual setup, no dependency management, no configuration headaches.

## 📖 Installation Methods Comparison

| Feature | Full Installer | Standalone Installer | Manual Install |
|---------|----------------|---------------------|----------------|
| **User effort** | One command | One command | Multiple steps |
| **Dependencies** | Auto-installs | Uses system packages | Manual install |
| **Speed** | Fast | Very fast | Slow |
| **Compatibility** | High | Highest | Varies |
| **Maintenance** | Auto-updates | Self-contained | Manual updates |
| **Size** | Smaller | Larger | Smallest |

## 🛠️ Full Installer (`install.sh`)

The comprehensive installer that handles everything automatically.

### What It Does

1. **🔍 System Detection**
   - Detects OS, distribution, and architecture
   - Identifies available package managers
   - Checks for existing tools

2. **📦 Dependency Management**
   - Installs missing prerequisites (Python, Git, curl, unzip)
   - Sets up uv package manager
   - Handles distribution-specific package installation

3. **🏗️ Building Process**
   - Downloads source code
   - Installs Python dependencies
   - Attempts to build standalone executable with PyInstaller
   - Falls back to wrapper script if build fails

4. **⚙️ Configuration**
   - Adds to PATH automatically
   - Creates configuration template
   - Sets up shell integration

5. **✅ Verification**
   - Tests installation
   - Provides detailed completion information

### Supported Systems

#### Linux Distributions
- **Ubuntu/Debian** - APT package manager
- **CentOS/RHEL/Fedora** - DNF/YUM package manager
- **Arch Linux/Manjaro** - Pacman package manager
- **Alpine Linux** - APK package manager

#### macOS
- **Homebrew** integration
- Automatic Homebrew installation if missing
- Apple Silicon and Intel support

### Usage

```bash
# Basic installation
curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.sh | bash

# With custom installation directory
curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.sh | INSTALL_DIR=/usr/local/bin bash

# Verbose installation
curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.sh | bash -s -- --verbose
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `INSTALL_DIR` | `$HOME/.local/bin` | Installation directory |
| `TEMP_DIR` | `/tmp/gsai-install-$$` | Temporary build directory |
| `PYTHON_MIN_VERSION` | `3.10` | Minimum Python version |

## 🎯 Standalone Installer (`standalone-install.sh`)

Ultra-portable installer that works without any user dependencies.

### What Makes It Special

1. **Zero Prerequisites**
   - No need to install uv, git, or specific Python versions
   - Works with minimal system packages
   - Automatic fallbacks for missing tools

2. **Self-Contained**
   - Creates portable Python environment
   - Bundles all dependencies
   - Works offline after initial download

3. **Maximum Compatibility**
   - Works on very old systems
   - Handles broken package managers
   - Multiple fallback strategies

4. **Bulletproof Installation**
   - Recovers from partial failures
   - Comprehensive error handling
   - Detailed logging

### How It Works

```bash
# Download source
curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/standalone-install.sh | bash
```

The installer:
1. Creates `~/.gsai/` directory for all components
2. Downloads and extracts source code
3. Creates portable Python environment (if possible)
4. Installs minimal required packages
5. Creates smart launcher script that handles different scenarios
6. Sets up PATH and configuration

### Fallback Strategy

The standalone installer has multiple fallback strategies:

```
PyInstaller executable ──→ Portable Python env ──→ System Python ──→ Error with instructions
```

## 💻 Windows Installer (`install.ps1`)

PowerShell-based installer for Windows systems.

### Features

- **Package Manager Integration**: Supports winget, Chocolatey, Scoop
- **Automatic Prerequisites**: Installs Python, Git if missing
- **PATH Management**: Automatically configures Windows PATH
- **UAC Handling**: Prompts for elevation when needed
- **Multiple Install Modes**: User vs. system-wide installation

### Usage

```powershell
# Basic installation
iwr -useb https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.ps1 | iex

# System-wide installation (requires admin)
iwr -useb https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.ps1 | iex -Global

# Custom installation directory
$env:INSTALL_DIR="C:\Tools\GitStart"; iwr -useb https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.ps1 | iex
```

### Prerequisites Handling

The Windows installer automatically handles:
- **Python 3.10+** - Via winget, Chocolatey, or manual prompt
- **Git** - Via package managers or manual download
- **PowerShell 5.1+** - Version check and upgrade prompt
- **Windows Defender** - Exclusion setup if needed

## 🔧 Installation Process Details

### Step-by-Step Breakdown

#### 1. System Detection (All Installers)
```bash
# Detects:
- Operating system (Linux, macOS, Windows)
- Architecture (x64, ARM64, x86)
- Distribution (Ubuntu, CentOS, etc.)
- Available package managers
- Existing tools and versions
```

#### 2. Prerequisites Installation
```bash
# Linux (example for Ubuntu)
sudo apt-get update -qq
sudo apt-get install -y curl unzip python3 python3-pip python3-venv

# macOS
brew install python@3.12 git curl

# Windows
winget install Python.Python.3.12 Git.Git
```

#### 3. uv Installation (Full Installer Only)
```bash
# Installs uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
```

#### 4. Source Download
```bash
# Downloads and extracts source
curl -L "https://github.com/your-org/gitstart-cli/archive/refs/heads/main.zip" -o source.zip
unzip -q source.zip
cd gitstart-cli-main
```

#### 5. Build Process
```bash
# Method 1: PyInstaller (Full Installer)
uv sync
uv run python build_simple.py  # Creates dist/gsai

# Method 2: uv tool (Fallback)
uv tool install .

# Method 3: Wrapper Script (Final Fallback)
# Creates intelligent wrapper that manages environment
```

#### 6. Installation
```bash
# Copy executable or create wrapper
cp dist/gsai $HOME/.local/bin/gsai
chmod +x $HOME/.local/bin/gsai

# Configure PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

#### 7. Configuration Setup
```bash
# Create config directory and template
mkdir -p ~/.ai/gsai
cat > ~/.ai/gsai/.env << 'EOF'
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
APPROVAL_MODE=suggest
EOF
chmod 600 ~/.ai/gsai/.env
```

## ✅ Post-Installation

After any installer completes:

### 1. Verify Installation
```bash
# Check if gsai is available
gsai --version

# Check configuration
gsai status
```

### 2. Configure API Keys
```bash
# Interactive configuration
gsai configure

# Or edit manually
nano ~/.ai/gsai/.env
```

### 3. Start Using
```bash
# Navigate to your project
cd your-project

# Start AI coding session
gsai chat
```

## 🚨 Troubleshooting

### Common Issues

#### "command not found: gsai"
```bash
# Add to current session
export PATH="$HOME/.local/bin:$PATH"

# Check installation
ls -la ~/.local/bin/gsai

# Restart terminal or reload shell
source ~/.bashrc
```

#### Permission Denied
```bash
# Fix permissions
chmod +x ~/.local/bin/gsai

# Or reinstall with correct permissions
curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.sh | bash
```

#### Python Version Issues
```bash
# Check Python version
python3 --version

# If too old, reinstaller will handle it automatically
curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.sh | bash
```

#### Build Failures
```bash
# Try standalone installer instead
curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/standalone-install.sh | bash
```

### Platform-Specific Issues

#### Linux: Package Manager Issues
```bash
# If apt/yum fails, try standalone installer
curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/standalone-install.sh | bash
```

#### macOS: Homebrew Issues
```bash
# Installer will try to install Homebrew automatically
# If that fails, install manually then rerun installer
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Windows: Execution Policy
```powershell
# If PowerShell blocks execution
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then retry installation
iwr -useb https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.ps1 | iex
```

## 🔄 Updates and Maintenance

### Auto-Update (Future Feature)
```bash
# Check for updates
gsai update

# Force reinstall
curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.sh | bash
```

### Manual Update
```bash
# Rerun installer (safe to run multiple times)
curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.sh | bash
```

### Uninstallation
```bash
# Remove executable
rm ~/.local/bin/gsai

# Remove configuration (optional)
rm -rf ~/.ai/gsai

# Remove from PATH (edit shell profiles)
nano ~/.bashrc  # Remove the PATH line
```

## 📊 Installer Comparison

### When to Use Each Installer

#### Use Full Installer (`install.sh`) When:
- ✅ You have sudo access
- ✅ You want the fastest execution
- ✅ You want automatic package management
- ✅ You're on a modern system with good package managers

#### Use Standalone Installer (`standalone-install.sh`) When:
- ✅ You don't have sudo access
- ✅ You're on an older/restricted system
- ✅ Package managers are broken or unavailable
- ✅ You want maximum compatibility
- ✅ You prefer self-contained installations

#### Use Windows Installer (`install.ps1`) When:
- ✅ You're on Windows
- ✅ You want PowerShell integration
- ✅ You want Windows-specific features (PATH, registry, etc.)

## 🎯 Advanced Usage

### Custom Installation Options

#### Full Installer Environment Variables
```bash
# Custom installation directory
export INSTALL_DIR="/usr/local/bin"

# Custom Python version requirement
export PYTHON_MIN_VERSION="3.12"

# Skip package manager updates
export SKIP_PACKAGE_UPDATE=1

curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.sh | bash
```

#### Standalone Installer Options
```bash
# Force system Python (skip portable env)
export FORCE_SYSTEM_PYTHON=1

# Custom gsai home directory
export GSAI_HOME="$HOME/mytools/gsai"

curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/standalone-install.sh | bash
```

### Offline Installation

For environments without internet access:

1. **Download installer script**:
   ```bash
   curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.sh > install.sh
   ```

2. **Modify URLs** in script to point to local mirrors

3. **Run installer**:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

### Container/Docker Installation

```dockerfile
# Dockerfile example
FROM ubuntu:22.04
RUN curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.sh | bash
ENV PATH="/root/.local/bin:$PATH"
ENTRYPOINT ["gsai"]
```

---

**🎉 That's it!** The installers handle everything else automatically. Users can go from zero to AI-powered coding in under 2 minutes with a single command.