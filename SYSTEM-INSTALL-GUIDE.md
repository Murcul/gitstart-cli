# GitStart CoPilot CLI - System-Wide Installation Guide

Complete guide for installing GitStart CoPilot CLI globally so `gsai` is accessible from anywhere.

## 🎯 Installation Locations

### Windows
- **System-wide**: `C:\Program Files\GitStart\gsai.exe`
- **User-only**: `%LOCALAPPDATA%\GitStart\gsai.exe`

### Linux/macOS
- **System-wide**: `/usr/local/bin/gsai`
- **User-only**: `~/.local/bin/gsai`

## 🚀 One-Command System Installation

### Windows (Run as Administrator)
```powershell
# System-wide installation (requires admin)
iwr -useb https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.ps1 | iex

# Or force system-wide
iwr -useb https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.ps1 | iex -SystemWide
```

### Linux/macOS
```bash
# System-wide installation (will prompt for sudo)
curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.sh | bash

# Or force system-wide
curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.sh | sudo INSTALL_DIR=/usr/local/bin bash
```

### Zero-Dependency (Standalone)
```bash
# System-wide standalone installer
curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/standalone-install.sh | bash
```

## 🔧 Installation Behavior

### Default Behavior (NEW)

**All installers now default to system-wide installation:**

1. **Windows**: Installs to `Program Files` and adds to system PATH
2. **Linux/macOS**: Installs to `/usr/local/bin` (system-wide)
3. **Fallback**: If no admin/sudo access, falls back to user installation

### Interactive Prompts

If you don't have admin privileges, installers will ask:

**Windows:**
```
GitStart CoPilot CLI will be installed system-wide for all users.
This requires administrator privileges.
Install system-wide (requires admin) [Y] or user-only [N]? (Y/n)
```

**Linux/macOS:**
```
GitStart CoPilot CLI can be installed system-wide (/usr/local/bin) or user-only (~/.local/bin)
System-wide installation makes 'gsai' available for all users
Install system-wide (requires sudo) [Y/n]?
```

## 📍 PATH Configuration

### System-Wide Installation
- **Windows**: Added to Machine PATH (all users)
- **Linux/macOS**: Uses `/usr/local/bin` (already in system PATH)
- **Result**: `gsai` works for all users from any terminal

### User Installation
- **Windows**: Added to User PATH
- **Linux/macOS**: Added to shell profiles (~/.bashrc, ~/.zshrc, ~/.profile)
- **Result**: `gsai` works for current user from any terminal

## 🛠️ Manual Installation Options

### Force System-Wide

**Windows (as Administrator):**
```powershell
$env:INSTALL_DIR="C:\Program Files\GitStart"
iwr -useb https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.ps1 | iex
```

**Linux/macOS:**
```bash
sudo INSTALL_DIR=/usr/local/bin bash <(curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.sh)
```

### Force User-Only

**Windows:**
```powershell
$env:INSTALL_DIR="$env:LOCALAPPDATA\GitStart"
iwr -useb https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.ps1 | iex
```

**Linux/macOS:**
```bash
INSTALL_DIR="$HOME/.local/bin" bash <(curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.sh)
```

## 🔍 Verify Installation

After installation, `gsai` should be globally accessible:

```bash
# Check if gsai is in PATH
gsai --version

# Check installation location
which gsai          # Linux/macOS
where gsai          # Windows

# Test basic functionality
gsai --help
gsai status
```

## 🌍 Global Access Benefits

### System-Wide Installation Benefits:
✅ **All users** can use `gsai`  
✅ **No per-user setup** required  
✅ **Consistent location** across systems  
✅ **Automatic PATH** configuration  
✅ **Enterprise deployment** friendly  

### Commands Work Everywhere:
```bash
# From any directory
cd /path/to/project
gsai chat

# From any user (system install)
sudo -u otheruser gsai --help

# In scripts and automation
#!/bin/bash
gsai status && gsai chat
```

## 🔧 Advanced Configuration

### Custom Installation Directory

**Windows:**
```powershell
# Install to custom location
$env:INSTALL_DIR="C:\Tools\GitStart"
iwr -useb https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.ps1 | iex
```

**Linux/macOS:**
```bash
# Install to custom location
INSTALL_DIR="/opt/gitstart/bin" bash <(curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.sh)
```

### Silent Installation

**Windows (System-wide, no prompts):**
```powershell
# Run elevated PowerShell, then:
iwr -useb https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.ps1 | iex -SystemWide
```

**Linux/macOS (System-wide, no prompts):**
```bash
# With sudo, no user prompts:
sudo bash <(curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.sh)
```

## 🏢 Enterprise Deployment

### Group Policy (Windows)
```powershell
# Deploy via Group Policy script
Set-ExecutionPolicy RemoteSigned -Force
iwr -useb https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.ps1 | iex -SystemWide
```

### Ansible/Puppet (Linux)
```yaml
# Ansible playbook example
- name: Install GitStart CoPilot CLI
  shell: |
    curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.sh | bash
  become: yes
  environment:
    INSTALL_DIR: /usr/local/bin
```

### Docker (System Container)
```dockerfile
FROM ubuntu:22.04
RUN curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.sh | bash
ENV PATH="/usr/local/bin:$PATH"
ENTRYPOINT ["gsai"]
```

## 🐛 Troubleshooting

### "gsai: command not found"

**Check Installation:**
```bash
# Linux/macOS
ls -la /usr/local/bin/gsai
ls -la ~/.local/bin/gsai

# Windows
dir "C:\Program Files\GitStart\gsai.exe"
dir "%LOCALAPPDATA%\GitStart\gsai.exe"
```

**Check PATH:**
```bash
# Linux/macOS
echo $PATH | grep -o '/usr/local/bin\|\.local/bin'

# Windows
echo $env:PATH -split ';' | Select-String "GitStart"
```

**Fix PATH:**
```bash
# Linux/macOS - add to current session
export PATH="/usr/local/bin:$PATH"

# Windows - add to current session
$env:PATH = "C:\Program Files\GitStart;$env:PATH"
```

### Permission Issues

**Windows:**
- Run PowerShell as Administrator
- Or install to user directory: `$env:INSTALL_DIR="$env:LOCALAPPDATA\GitStart"`

**Linux/macOS:**
- Use sudo for system install: `sudo bash <(curl -sSL ...)`
- Or install to user directory: `INSTALL_DIR="$HOME/.local/bin"`

### Multiple Installations

If you have both user and system installations:

```bash
# Check all locations
# Linux/macOS
ls -la /usr/local/bin/gsai ~/.local/bin/gsai

# Windows  
dir "C:\Program Files\GitStart\gsai.exe" "%LOCALAPPDATA%\GitStart\gsai.exe"

# Remove user installation if you want system-only
rm ~/.local/bin/gsai  # Linux/macOS
Remove-Item "$env:LOCALAPPDATA\GitStart\gsai.exe"  # Windows
```

## 📊 Installation Summary

| Method | Location | Users | PATH | Admin Required |
|--------|----------|-------|------|----------------|
| **Default Installer** | System | All | Automatic | Yes |
| **User Fallback** | User Dir | Current | Shell Profiles | No |
| **Force System** | System | All | Automatic | Yes |
| **Force User** | User Dir | Current | Shell Profiles | No |
| **Custom Location** | Custom | Depends | Manual | Maybe |

## 🎉 Success Verification

After system-wide installation, you should see:

```bash
$ gsai --version
GitStart CoPilot CLI v1.0.0

$ which gsai
/usr/local/bin/gsai

$ gsai status
✅ GitStart CoPilot CLI is ready
✅ Configuration found
✅ API keys configured
✅ System installation detected
```

---

**The new default behavior makes gsai globally accessible for all users with a single installation command!**