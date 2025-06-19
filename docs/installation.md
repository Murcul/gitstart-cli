# Installation Guide

This guide covers all installation methods for GitStart CoPilot CLI across different platforms.

## 🎯 Quick Installation (Recommended)

### Download Pre-built Executables

The easiest way to install GitStart CoPilot CLI is to download a pre-built executable from our [releases page](../releases).

**Linux:**
```bash
# Download and install
curl -L -o gsai https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-linux-x86_64
chmod +x gsai
sudo mv gsai /usr/local/bin/
```

**macOS:**
```bash
# Download and install
curl -L -o gsai https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-macos-x86_64
chmod +x gsai
sudo mv gsai /usr/local/bin/
```

**Windows:**
```powershell
# Download from releases page and add to PATH
# Or use winget (if available):
# winget install GitStart.CoPilotCLI
```

### Verify Installation
```bash
gsai --version
gsai --help
```

## 🔧 Platform-Specific Guides

For detailed platform-specific instructions:

- **[Linux Installation Guide](installation-linux.md)** - Ubuntu, Debian, CentOS, Arch, etc.
- **[macOS Installation Guide](installation-macos.md)** - Homebrew, manual installation
- **[Windows Installation Guide](installation-windows.md)** - PowerShell, manual installation

## 🛠️ Installation from Source

### Prerequisites

- **Python 3.12+** (required)
- **Git** (for cloning repository)
- **uv** (Python package manager - will be installed automatically)

### Install with uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/gitstart-cli.git
cd gitstart-cli

# Install uv if not present
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies and CLI
uv sync
uv tool install .
```

### Install with pip

```bash
# Clone the repository
git clone https://github.com/your-org/gitstart-cli.git
cd gitstart-cli

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install
pip install -e .
```

### Development Installation

For development and contributing:

```bash
# Clone repository
git clone https://github.com/your-org/gitstart-cli.git
cd gitstart-cli

# Install with development dependencies
uv sync --dev

# Run directly
uv run gsai --help

# Or install globally
uv tool install .
```

## 📦 Package Managers

### Homebrew (macOS/Linux)

```bash
# Add tap (if available)
brew tap gitstart/cli
brew install gsai

# Or install from formula
brew install gitstart/cli/gsai
```

### APT (Ubuntu/Debian)

```bash
# Add repository (if available)
curl -fsSL https://packages.gitstart.com/gpg | sudo apt-key add -
echo "deb https://packages.gitstart.com/apt stable main" | sudo tee /etc/apt/sources.list.d/gitstart.list

# Install
sudo apt update
sudo apt install gsai
```

### Snap (Linux)

```bash
# Install from snap store (if available)
sudo snap install gsai
```

### AUR (Arch Linux)

```bash
# Install from AUR (if available)
yay -S gsai
# or
paru -S gsai
```

## 🐳 Container Installation

### Docker

```bash
# Pull image
docker pull gitstart/copilot-cli:latest

# Run container
docker run -it --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  gitstart/copilot-cli:latest gsai chat

# Create alias for convenience
echo 'alias gsai="docker run -it --rm -v $(pwd):/workspace -w /workspace gitstart/copilot-cli:latest gsai"' >> ~/.bashrc
```

### Podman

```bash
# Pull and run with Podman
podman pull gitstart/copilot-cli:latest
podman run -it --rm -v $(pwd):/workspace:Z -w /workspace gitstart/copilot-cli:latest gsai chat
```

## 🔐 Post-Installation Setup

### 1. Configure API Keys

After installation, configure your API keys:

```bash
gsai configure
```

This will prompt you to enter:
- OpenAI API Key (optional)
- Anthropic API Key (optional)
- Approval mode preference
- Other settings

### 2. Verify Installation

```bash
# Check version
gsai --version

# Check configuration
gsai status

# Test basic functionality
gsai --help
```

### 3. First Run

Try your first AI coding session:

```bash
# Navigate to a project directory
cd your-project

# Start interactive session
gsai chat
```

## 🔄 Updating

### Pre-built Executables

Download the latest version from [releases](../releases) and replace your existing installation.

### Package Managers

```bash
# Homebrew
brew upgrade gsai

# APT
sudo apt update && sudo apt upgrade gsai

# Snap
sudo snap refresh gsai

# uv tool
uv tool upgrade gsai
```

### From Source

```bash
cd gitstart-cli
git pull origin main
uv tool install . --force
```

## 🗑️ Uninstallation

### Remove Executable

```bash
# If installed to /usr/local/bin
sudo rm /usr/local/bin/gsai

# If installed with uv tool
uv tool uninstall gsai
```

### Remove Configuration

```bash
# Remove configuration directory
rm -rf ~/.ai/gsai
```

### Package Managers

```bash
# Homebrew
brew uninstall gsai

# APT
sudo apt remove gsai

# Snap
sudo snap remove gsai
```

## ❗ Common Issues

### Python Version Issues

GitStart CoPilot requires Python 3.12+. If you have an older version:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.12
```

**macOS:**
```bash
brew install python@3.12
```

### Permission Issues

If you get permission errors:

```bash
# Use user installation
pip install --user -e .

# Or fix permissions
sudo chown -R $(whoami) /usr/local/bin
```

### PATH Issues

If `gsai` command is not found:

```bash
# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"

# Reload shell
source ~/.bashrc
```

## 🆘 Getting Help

- **Installation Issues:** See [Troubleshooting Guide](troubleshooting.md)
- **Platform-specific Help:** Check platform guides ([Linux](installation-linux.md), [macOS](installation-macos.md), [Windows](installation-windows.md))
- **Configuration Help:** See [Configuration Guide](configuration.md)

---

**Next Steps:** After installation, check out the [Quick Start Guide](quick-start.md) to begin using GitStart CoPilot CLI!