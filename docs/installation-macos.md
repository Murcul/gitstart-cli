# macOS Installation Guide

Complete installation guide for GitStart CoPilot CLI on macOS.

## 🚀 Quick Installation

### Method 1: Download Pre-built Binary (Recommended)

```bash
# Download latest release
curl -L -o gsai https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-macos-x86_64

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
curl -L https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-macos-x86_64 | sudo tee /usr/local/bin/gsai > /dev/null && sudo chmod +x /usr/local/bin/gsai
```

## 🍺 Homebrew Installation (Recommended)

### Install via Homebrew

```bash
# Add GitStart tap
brew tap gitstart/cli

# Install gsai
brew install gsai

# Verify installation
gsai --version
```

### Install from Formula URL

```bash
# Install directly from formula
brew install https://raw.githubusercontent.com/your-org/gitstart-cli/main/homebrew/gsai.rb
```

### Update via Homebrew

```bash
# Update tap
brew update

# Upgrade gsai
brew upgrade gsai
```

## 📦 Package Installation

### Download .pkg Installer

1. Go to [Releases Page](https://github.com/your-org/gitstart-cli/releases)
2. Download `gsai-macos-installer.pkg`
3. Double-click to install
4. Follow installation wizard

### Command Line .pkg Installation

```bash
# Download package
curl -L -o gsai-installer.pkg https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-macos-installer.pkg

# Install package
sudo installer -pkg gsai-installer.pkg -target /
```

## 🛠️ Installation from Source

### Prerequisites

#### Install Xcode Command Line Tools
```bash
# Install Xcode CLI tools
xcode-select --install
```

#### Install Python 3.12+

**Option 1: Using Homebrew (Recommended)**
```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.12
brew install python@3.12

# Verify installation
python3.12 --version
```

**Option 2: Using pyenv**
```bash
# Install pyenv
brew install pyenv

# Install Python 3.12
pyenv install 3.12.0
pyenv global 3.12.0

# Add to shell profile
echo 'export PATH="$(pyenv root)/shims:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Option 3: Download from python.org**
1. Visit [python.org](https://www.python.org/downloads/macos/)
2. Download Python 3.12+ installer
3. Run installer package

#### Install uv Package Manager
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (add to ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"
source ~/.zshrc
```

### Build and Install

```bash
# Clone repository
git clone https://github.com/your-org/gitstart-cli.git
cd gitstart-cli

# Install dependencies and CLI
uv sync
uv tool install .

# Verify installation
gsai --version
```

## 🍎 macOS-Specific Considerations

### Architecture Support

#### Apple Silicon (M1/M2/M3)
```bash
# Download ARM64 binary (if available)
curl -L -o gsai https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-macos-arm64

# Or use Rosetta 2 for x86_64 binary
curl -L -o gsai https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-macos-x86_64
```

#### Universal Binary
```bash
# Download universal binary (supports both Intel and Apple Silicon)
curl -L -o gsai https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-macos-universal
```

### Security Considerations

#### Gatekeeper and Code Signing

When running the binary for the first time, you may see a security warning:

**Method 1: Using System Preferences**
1. Try to run `gsai`
2. Go to System Preferences → Security & Privacy
3. Click "Allow Anyway" next to the gsai warning

**Method 2: Command Line**
```bash
# Remove quarantine attribute
sudo xattr -rd com.apple.quarantine /usr/local/bin/gsai

# Or allow execution
sudo spctl --add /usr/local/bin/gsai
```

**Method 3: Temporary Override**
```bash
# Hold Control while running for first time
sudo ctrl+click /usr/local/bin/gsai
```

#### Notarization (For Distributed Binaries)

If you're distributing the binary:

```bash
# Check notarization status
spctl -a -t exec -vv /usr/local/bin/gsai

# Submit for notarization (developers only)
xcrun notarytool submit gsai.zip --keychain-profile "notarytool-profile" --wait
```

## ⚙️ Post-Installation Configuration

### 1. Shell Integration

#### Zsh (Default on macOS Catalina+)
```bash
# Add to ~/.zshrc
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc

# Enable completion
gsai --install-completion zsh
source ~/.zshrc
```

#### Bash
```bash
# Add to ~/.bash_profile
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bash_profile

# Enable completion
gsai --install-completion bash
source ~/.bash_profile
```

### 2. Configure API Keys

```bash
# Interactive configuration
gsai configure

# Or set environment variables
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"

# Make permanent (add to ~/.zshrc or ~/.bash_profile)
echo 'export OPENAI_API_KEY="your-openai-key"' >> ~/.zshrc
echo 'export ANTHROPIC_API_KEY="your-anthropic-key"' >> ~/.zshrc
```

### 3. macOS Keychain Integration (Optional)

Store API keys securely in macOS Keychain:

```bash
# Store API keys in keychain
security add-generic-password -a "$(whoami)" -s "gsai-openai" -w "your-openai-key"
security add-generic-password -a "$(whoami)" -s "gsai-anthropic" -w "your-anthropic-key"

# Create wrapper script to retrieve from keychain
cat > ~/.local/bin/gsai-with-keychain << 'EOF'
#!/bin/bash
export OPENAI_API_KEY=$(security find-generic-password -a "$(whoami)" -s "gsai-openai" -w 2>/dev/null)
export ANTHROPIC_API_KEY=$(security find-generic-password -a "$(whoami)" -s "gsai-anthropic" -w 2>/dev/null)
exec /usr/local/bin/gsai "$@"
EOF

chmod +x ~/.local/bin/gsai-with-keychain
```

## 🔄 Updating

### Homebrew Update
```bash
# Update all packages
brew update && brew upgrade

# Update only gsai
brew upgrade gsai
```

### Manual Binary Update
```bash
# Download latest version
curl -L -o gsai-new https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-macos-x86_64

# Replace existing
sudo mv gsai-new /usr/local/bin/gsai
sudo chmod +x /usr/local/bin/gsai
```

### From Source Update
```bash
cd gitstart-cli
git pull origin main
uv tool install . --force
```

## 🗑️ Uninstallation

### Remove Homebrew Installation
```bash
# Uninstall package
brew uninstall gsai

# Remove tap (optional)
brew untap gitstart/cli
```

### Remove Manual Installation
```bash
# Remove binary
sudo rm /usr/local/bin/gsai

# Remove configuration
rm -rf ~/.ai/gsai

# Remove from keychain (if used)
security delete-generic-password -a "$(whoami)" -s "gsai-openai"
security delete-generic-password -a "$(whoami)" -s "gsai-anthropic"
```

### Remove uv Tool Installation
```bash
# Remove tool
uv tool uninstall gsai

# Remove configuration
rm -rf ~/.ai/gsai
```

## 🐛 Troubleshooting

### Common Issues

#### "gsai" cannot be opened because the developer cannot be verified
```bash
# Solution 1: Remove quarantine
sudo xattr -rd com.apple.quarantine /usr/local/bin/gsai

# Solution 2: System Preferences approach
# 1. Try running gsai
# 2. Go to System Preferences → Security & Privacy
# 3. Click "Allow Anyway"
```

#### Command not found: gsai
```bash
# Check if gsai exists
ls -la /usr/local/bin/gsai

# Check PATH
echo $PATH

# Add to PATH if needed
export PATH="/usr/local/bin:$PATH"

# Make permanent
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

#### Permission denied
```bash
# Fix permissions
sudo chmod +x /usr/local/bin/gsai

# Or install to user directory
mkdir -p ~/.local/bin
mv gsai ~/.local/bin/
export PATH="$HOME/.local/bin:$PATH"
```

#### Python version issues
```bash
# Check Python version
python3 --version

# Install newer Python via Homebrew
brew install python@3.12

# Update PATH to use new Python
export PATH="/opt/homebrew/bin:$PATH"  # Apple Silicon
# or
export PATH="/usr/local/bin:$PATH"     # Intel Mac
```

#### SSL certificate problems
```bash
# Update certificates
brew install ca-certificates

# Or update Python certificates
/Applications/Python\ 3.12/Install\ Certificates.command
```

### macOS Version Compatibility

#### macOS Monterey (12.0+)
- Full compatibility
- All features supported

#### macOS Big Sur (11.0+)
- Compatible with minor limitations
- May require additional security permissions

#### macOS Catalina (10.15+)
- Basic compatibility
- May need to install Python 3.12 manually

#### Older macOS Versions (< 10.15)
- Not officially supported
- May work with manual Python installation

### Architecture-Specific Issues

#### Apple Silicon (M1/M2/M3) Issues
```bash
# Check architecture
uname -m  # Should return "arm64"

# Use ARM64 binary if available
curl -L -o gsai https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-macos-arm64

# Install Rosetta 2 if needed (for x86_64 binaries)
sudo softwareupdate --install-rosetta
```

#### Intel Mac Issues
```bash
# Check architecture
uname -m  # Should return "x86_64"

# Use x86_64 binary
curl -L -o gsai https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-macos-x86_64
```

## 📱 Integration with macOS Tools

### Spotlight Integration
```bash
# Make gsai searchable in Spotlight
sudo mdutil -i on /usr/local/bin
```

### Automator Integration
Create Automator workflows to run gsai commands:

1. Open Automator
2. Create new "Quick Action"
3. Add "Run Shell Script" action
4. Set script to: `/usr/local/bin/gsai chat`

### Terminal Integration
```bash
# Add custom terminal profile for gsai
# Terminal → Preferences → Profiles → + (New)
# Set command to: /usr/local/bin/gsai chat
```

## 📞 Getting Help

For macOS-specific issues:

1. **Check Console.app** for system logs
2. **System Information** (Apple Menu → About This Mac → System Report)
3. **Activity Monitor** to check if gsai is running
4. **Terminal.app** for command-line debugging

**Common Locations:**
- Configuration: `~/.ai/gsai/`
- Binary: `/usr/local/bin/gsai` or `/opt/homebrew/bin/gsai`
- Homebrew logs: `brew --cache`

---

**Next:** [Quick Start Guide](quick-start.md) | **See also:** [Configuration Guide](configuration.md)