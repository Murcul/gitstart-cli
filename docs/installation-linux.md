# Linux Installation Guide

Complete installation guide for GitStart CoPilot CLI on Linux distributions.

## 🚀 Quick Installation

### Method 1: Download Pre-built Binary (Recommended)

```bash
# Download latest release
curl -L -o gsai https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-linux-x86_64

# Make executable
chmod +x gsai

# Install system-wide
sudo mv gsai /usr/local/bin/

# Verify installation
gsai --version
```

### Method 2: One-liner Installation

```bash
# Download and install in one command
curl -L https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-linux-x86_64 | sudo tee /usr/local/bin/gsai > /dev/null && sudo chmod +x /usr/local/bin/gsai
```

## 📦 Distribution-Specific Installation

### Ubuntu / Debian

#### Option 1: APT Repository (Recommended)
```bash
# Add GPG key
curl -fsSL https://packages.gitstart.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/gitstart.gpg

# Add repository
echo "deb [signed-by=/usr/share/keyrings/gitstart.gpg] https://packages.gitstart.com/apt stable main" | sudo tee /etc/apt/sources.list.d/gitstart.list

# Update and install
sudo apt update
sudo apt install gsai
```

#### Option 2: DEB Package
```bash
# Download .deb package
wget https://github.com/your-org/gitstart-cli/releases/latest/download/gsai_linux_amd64.deb

# Install package
sudo dpkg -i gsai_linux_amd64.deb

# Fix dependencies if needed
sudo apt-get install -f
```

### CentOS / RHEL / Fedora

#### Option 1: RPM Package
```bash
# Download RPM package
wget https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-linux-x86_64.rpm

# Install with dnf (Fedora)
sudo dnf install ./gsai-linux-x86_64.rpm

# Install with yum (CentOS/RHEL)
sudo yum localinstall ./gsai-linux-x86_64.rpm
```

#### Option 2: YUM/DNF Repository
```bash
# Add repository
sudo tee /etc/yum.repos.d/gitstart.repo > /dev/null <<EOF
[gitstart]
name=GitStart Repository
baseurl=https://packages.gitstart.com/rpm
enabled=1
gpgcheck=1
gpgkey=https://packages.gitstart.com/gpg
EOF

# Install
sudo dnf install gsai  # Fedora
sudo yum install gsai  # CentOS/RHEL
```

### Arch Linux

#### Option 1: AUR Package
```bash
# Using yay
yay -S gsai

# Using paru
paru -S gsai

# Manual AUR installation
git clone https://aur.archlinux.org/gsai.git
cd gsai
makepkg -si
```

#### Option 2: Binary Installation
```bash
# Download and install binary
sudo pacman -S curl
curl -L -o gsai https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-linux-x86_64
chmod +x gsai
sudo mv gsai /usr/local/bin/
```

### openSUSE

```bash
# Add repository
sudo zypper addrepo https://packages.gitstart.com/opensuse gitstart

# Install
sudo zypper refresh
sudo zypper install gsai
```

### Alpine Linux

```bash
# Add repository
echo "https://packages.gitstart.com/alpine/v3.18/main" | sudo tee -a /etc/apk/repositories

# Add GPG key
wget -O /tmp/gitstart.pub https://packages.gitstart.com/alpine/gitstart.pub
sudo mv /tmp/gitstart.pub /etc/apk/keys/

# Install
sudo apk update
sudo apk add gsai
```

## 🛠️ Installation from Source

### Prerequisites Installation

#### Ubuntu / Debian
```bash
# Update package list
sudo apt update

# Install Python 3.12+
sudo apt install python3.12 python3.12-venv python3.12-dev

# Install git and curl
sudo apt install git curl

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### CentOS / RHEL / Fedora
```bash
# Install Python 3.12+ (may need EPEL repository)
sudo dnf install python3.12 python3.12-devel git curl

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Arch Linux
```bash
# Install dependencies
sudo pacman -S python git curl

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Build and Install

```bash
# Clone repository
git clone https://github.com/your-org/gitstart-cli.git
cd gitstart-cli

# Install with uv
uv sync
uv tool install .

# Verify installation
gsai --version
```

## 📋 Snap Package

### Install from Snap Store
```bash
# Install snapd if not present
sudo apt install snapd  # Ubuntu/Debian
sudo dnf install snapd  # Fedora
sudo pacman -S snapd    # Arch Linux

# Install gsai
sudo snap install gsai

# If using classic confinement
sudo snap install gsai --classic
```

## 🐳 Container Installation

### Docker
```bash
# Pull image
docker pull gitstart/copilot-cli:latest

# Create wrapper script
sudo tee /usr/local/bin/gsai > /dev/null <<'EOF'
#!/bin/bash
docker run -it --rm \
  -v "$(pwd):/workspace" \
  -v "$HOME/.ai:/root/.ai" \
  -w /workspace \
  gitstart/copilot-cli:latest gsai "$@"
EOF

# Make executable
sudo chmod +x /usr/local/bin/gsai
```

### Podman
```bash
# Pull image
podman pull gitstart/copilot-cli:latest

# Create wrapper script
sudo tee /usr/local/bin/gsai > /dev/null <<'EOF'
#!/bin/bash
podman run -it --rm \
  -v "$(pwd):/workspace:Z" \
  -v "$HOME/.ai:/root/.ai:Z" \
  -w /workspace \
  gitstart/copilot-cli:latest gsai "$@"
EOF

# Make executable
sudo chmod +x /usr/local/bin/gsai
```

## ⚙️ Post-Installation Configuration

### 1. Add to PATH (if needed)
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Reload shell
source ~/.bashrc
```

### 2. Configure API Keys
```bash
# Interactive configuration
gsai configure

# Or set environment variables
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"

# Make permanent (add to ~/.bashrc)
echo 'export OPENAI_API_KEY="your-openai-key"' >> ~/.bashrc
echo 'export ANTHROPIC_API_KEY="your-anthropic-key"' >> ~/.bashrc
```

### 3. Shell Completion (Optional)
```bash
# Generate completion script
gsai --install-completion

# Or manually add to ~/.bashrc
gsai --show-completion >> ~/.bashrc
source ~/.bashrc
```

## 🔄 Updating

### Binary Installation
```bash
# Download latest version
curl -L -o gsai-new https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-linux-x86_64

# Replace existing installation
sudo mv gsai-new /usr/local/bin/gsai
sudo chmod +x /usr/local/bin/gsai
```

### Package Manager Updates
```bash
# APT
sudo apt update && sudo apt upgrade gsai

# DNF/YUM
sudo dnf update gsai

# Pacman (if from AUR)
yay -Syu gsai

# Snap
sudo snap refresh gsai
```

### From Source
```bash
cd gitstart-cli
git pull origin main
uv tool install . --force
```

## 🗑️ Uninstallation

### Remove Binary
```bash
# Remove executable
sudo rm /usr/local/bin/gsai

# Remove configuration
rm -rf ~/.ai/gsai
```

### Package Manager Removal
```bash
# APT
sudo apt remove gsai
sudo apt autoremove

# DNF/YUM
sudo dnf remove gsai

# Pacman
sudo pacman -Rs gsai

# Snap
sudo snap remove gsai

# uv tool
uv tool uninstall gsai
```

## 🐛 Troubleshooting

### Common Issues

#### Permission Denied
```bash
# Fix permissions
sudo chmod +x /usr/local/bin/gsai

# Or install to user directory
mkdir -p ~/.local/bin
mv gsai ~/.local/bin/
export PATH="$HOME/.local/bin:$PATH"
```

#### Command Not Found
```bash
# Check if gsai is in PATH
which gsai

# Add to PATH if needed
export PATH="/usr/local/bin:$PATH"

# Make permanent
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
```

#### Python Version Issues
```bash
# Check Python version
python3 --version

# Install Python 3.12+ if needed
sudo apt install python3.12  # Ubuntu/Debian
sudo dnf install python3.12  # Fedora
```

#### SSL Certificate Issues
```bash
# Update certificates
sudo apt update && sudo apt install ca-certificates  # Ubuntu/Debian
sudo dnf update ca-certificates                       # Fedora
```

### Distribution-Specific Issues

#### Ubuntu/Debian: Missing Dependencies
```bash
sudo apt install python3.12-venv python3.12-dev build-essential
```

#### CentOS/RHEL: Python 3.12 Not Available
```bash
# Enable EPEL repository
sudo dnf install epel-release

# Or compile from source
wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz
tar xzf Python-3.12.0.tgz
cd Python-3.12.0
./configure --enable-optimizations
make -j$(nproc)
sudo make altinstall
```

#### Arch Linux: AUR Build Fails
```bash
# Update keyring
sudo pacman -S archlinux-keyring

# Clear package cache
yay -Sc

# Retry installation
yay -S gsai
```

## 📞 Getting Help

For Linux-specific issues:

1. **Check System Logs:**
   ```bash
   journalctl -u gsai  # If installed as service
   dmesg | grep gsai
   ```

2. **Verify Dependencies:**
   ```bash
   ldd /usr/local/bin/gsai  # Check shared libraries
   ```

3. **Common Locations:**
   - Configuration: `~/.ai/gsai/`
   - Logs: `~/.ai/gsai/logs/` (if any)
   - Binary: `/usr/local/bin/gsai` or `~/.local/bin/gsai`

4. **Community Support:**
   - GitHub Issues
   - Distribution-specific forums
   - Stack Overflow with `gitstart-cli` tag

---

**Next:** [Quick Start Guide](quick-start.md) | **See also:** [Configuration Guide](configuration.md)