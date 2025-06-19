# GitStart CoPilot CLI - Public Installation

**AI-powered coding assistant with embedded API keys - ready to use immediately!**

## 🚀 One-Command Installation

### Windows
```powershell
iwr -useb https://github.com/Murcul/gitstart-cli/releases/latest/download/install.ps1 | iex
```

### Linux/macOS
```bash
curl -sSL https://github.com/Murcul/gitstart-cli/releases/latest/download/install.sh | bash
```

### Zero-Dependency Installer (works on restricted systems)
```bash
curl -sSL https://github.com/Murcul/gitstart-cli/releases/latest/download/standalone-install.sh | bash
```

## 📦 Direct Downloads

Download pre-built executables (no installation required):

- [Windows (x64)](https://github.com/Murcul/gitstart-cli/releases/latest/download/gsai-windows-x86_64.zip)
- [macOS (Intel/Apple Silicon)](https://github.com/Murcul/gitstart-cli/releases/latest/download/gsai-macos-x86_64.zip)
- [Linux (x64)](https://github.com/Murcul/gitstart-cli/releases/latest/download/gsai-linux-x86_64.zip)

Extract and run directly - no setup required!

## 🎯 What You Get

✅ **Instant Setup** - Works immediately with embedded API keys  
✅ **System-Wide Access** - `gsai` command available globally  
✅ **Cross-Platform** - Windows, macOS, Linux support  
✅ **Zero Dependencies** - No Python or package installation needed  
✅ **AI Coding Assistant** - Interactive coding sessions with AI  

## 🔧 Quick Start

After installation:

```bash
# Check installation
gsai --version

# Start AI coding session
gsai chat

# Get help
gsai --help

# Check configuration
gsai status
```

## 🏢 Enterprise Installation

### Silent Installation (Windows)
```powershell
# Run as Administrator for system-wide install
iwr -useb https://github.com/Murcul/gitstart-cli/releases/latest/download/install.ps1 | iex
```

### Automated Deployment (Linux/macOS)
```bash
# System-wide installation
sudo bash <(curl -sSL https://github.com/Murcul/gitstart-cli/releases/latest/download/install.sh)
```

### Docker Usage
```bash
# Run in container
docker run -it --rm -v "$(pwd):/workspace" -w /workspace \
  gitstart/copilot-cli:latest gsai chat
```

## 🔑 API Keys

**This build includes embedded API keys** for immediate use. You can also configure your own:

```bash
gsai configure
```

Get your own keys:
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/

## 📍 Installation Locations

### System-Wide (Default)
- **Windows**: `C:\Program Files\GitStart\gsai.exe`
- **Linux/macOS**: `/usr/local/bin/gsai`

### User-Only (Fallback)
- **Windows**: `%LOCALAPPDATA%\GitStart\gsai.exe`
- **Linux/macOS**: `~/.local/bin/gsai`

## 🛠️ Version-Specific Installation

Replace `latest` with a specific version tag:

```bash
# Install specific version
curl -sSL https://github.com/Murcul/gitstart-cli/releases/download/v1.0.0/install.sh | bash
```

## 🐛 Troubleshooting

### "gsai: command not found"
```bash
# Restart terminal or reload PATH
source ~/.bashrc  # Linux/macOS
# Or restart PowerShell (Windows)

# Check installation
which gsai        # Linux/macOS
where gsai        # Windows
```

### Permission Issues
```bash
# Windows: Run PowerShell as Administrator
# Linux/macOS: Installer will prompt for sudo when needed
```

### Multiple Installations
```bash
# Remove user installation if you want system-only
rm ~/.local/bin/gsai                              # Linux/macOS
Remove-Item "$env:LOCALAPPDATA\GitStart\gsai.exe" # Windows
```

## 🔗 All Releases

View all available versions: [Releases Page](https://github.com/Murcul/gitstart-cli/releases)

## ❓ Support

Having issues? Check the [troubleshooting guide](https://github.com/Murcul/gitstart-cli/releases/latest/download/INSTALL.md) included with each release.

---

**Note**: This software is distributed from a private repository. Executables and installers are publicly available for easy distribution while keeping source code private.

**Repository**: https://github.com/Murcul/gitstart-cli (private)  
**Public Releases**: https://github.com/Murcul/gitstart-cli/releases