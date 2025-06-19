# Windows Installation Guide

Complete installation guide for GitStart CoPilot CLI on Windows.

## 🚀 Quick Installation

### Method 1: Download Pre-built Executable (Recommended)

1. **Download the latest Windows executable:**
   - Go to [Releases Page](https://github.com/your-org/gitstart-cli/releases)
   - Download `gsai-windows-x86_64.exe`

2. **Install system-wide:**
   ```powershell
   # Create installation directory
   New-Item -ItemType Directory -Force -Path "C:\Program Files\GitStart"
   
   # Move executable (run as Administrator)
   Move-Item "gsai-windows-x86_64.exe" "C:\Program Files\GitStart\gsai.exe"
   
   # Add to PATH
   $env:PATH += ";C:\Program Files\GitStart"
   [Environment]::SetEnvironmentVariable("PATH", $env:PATH, [EnvironmentVariableTarget]::Machine)
   ```

3. **Or install for current user:**
   ```powershell
   # Create user installation directory
   New-Item -ItemType Directory -Force -Path "$env:LOCALAPPDATA\GitStart"
   
   # Move executable
   Move-Item "gsai-windows-x86_64.exe" "$env:LOCALAPPDATA\GitStart\gsai.exe"
   
   # Add to user PATH
   $userPath = [Environment]::GetEnvironmentVariable("PATH", [EnvironmentVariableTarget]::User)
   [Environment]::SetEnvironmentVariable("PATH", "$userPath;$env:LOCALAPPDATA\GitStart", [EnvironmentVariableTarget]::User)
   ```

### Method 2: One-liner Installation (PowerShell)

```powershell
# Download and install (run as Administrator)
Invoke-WebRequest -Uri "https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-windows-x86_64.exe" -OutFile "$env:TEMP\gsai.exe"
New-Item -ItemType Directory -Force -Path "C:\Program Files\GitStart"
Move-Item "$env:TEMP\gsai.exe" "C:\Program Files\GitStart\gsai.exe"
$env:PATH += ";C:\Program Files\GitStart"
[Environment]::SetEnvironmentVariable("PATH", $env:PATH, [EnvironmentVariableTarget]::Machine)
```

## 📦 Package Manager Installation

### Windows Package Manager (winget)

```powershell
# Install via winget (if available)
winget install GitStart.CoPilotCLI

# Or from manifest
winget install --manifest https://github.com/your-org/gitstart-cli/releases/latest/download/gsai.yaml
```

### Chocolatey

```powershell
# Install Chocolatey if not present
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Install gsai
choco install gsai
```

### Scoop

```powershell
# Install Scoop if not present
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

# Add bucket and install
scoop bucket add gitstart https://github.com/your-org/scoop-bucket
scoop install gsai
```

## 🛠️ Installation from Source

### Prerequisites

#### Install Python 3.12+

**Option 1: From python.org (Recommended)**
1. Download Python 3.12+ from [python.org](https://www.python.org/downloads/windows/)
2. Run installer with "Add Python to PATH" checked
3. Verify installation:
   ```powershell
   python --version
   ```

**Option 2: From Microsoft Store**
```powershell
# Install from Microsoft Store
winget install Python.Python.3.12
```

**Option 3: Using Chocolatey**
```powershell
choco install python312
```

#### Install Git

**Option 1: Git for Windows**
1. Download from [git-scm.com](https://git-scm.com/download/win)
2. Run installer with default settings

**Option 2: Package managers**
```powershell
# Chocolatey
choco install git

# Winget
winget install Git.Git
```

#### Install uv Package Manager

```powershell
# Install uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Add to PATH (usually done automatically)
$env:PATH += ";$env:USERPROFILE\.local\bin"
```

### Build and Install

```powershell
# Clone repository
git clone https://github.com/your-org/gitstart-cli.git
cd gitstart-cli

# Install dependencies and CLI
uv sync
uv tool install .

# Verify installation
gsai --version
```

## ⚙️ Windows-Specific Configuration

### PowerShell Execution Policy

If you encounter execution policy errors:

```powershell
# Check current policy
Get-ExecutionPolicy

# Allow local scripts (recommended)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or allow all scripts (less secure)
Set-ExecutionPolicy Unrestricted -Scope CurrentUser
```

### Windows Defender and Antivirus

If Windows Defender blocks the executable:

1. **Add exclusion:**
   - Open Windows Security
   - Go to Virus & threat protection
   - Add exclusion for `gsai.exe`

2. **Command line method:**
   ```powershell
   # Add exclusion (run as Administrator)
   Add-MpPreference -ExclusionPath "C:\Program Files\GitStart\gsai.exe"
   ```

### Environment Variables

#### Set via System Properties
1. Right-click "This PC" → Properties
2. Advanced system settings
3. Environment Variables
4. Add to System PATH: `C:\Program Files\GitStart`

#### Set via PowerShell
```powershell
# For current user
[Environment]::SetEnvironmentVariable("PATH", "$env:PATH;C:\Program Files\GitStart", [EnvironmentVariableTarget]::User)

# For all users (requires Administrator)
[Environment]::SetEnvironmentVariable("PATH", "$env:PATH;C:\Program Files\GitStart", [EnvironmentVariableTarget]::Machine)
```

### Configure API Keys

#### Method 1: Using gsai configure
```powershell
gsai configure
```

#### Method 2: PowerShell Environment Variables
```powershell
# Set for current session
$env:OPENAI_API_KEY = "sk-your-openai-key"
$env:ANTHROPIC_API_KEY = "sk-your-anthropic-key"

# Set permanently for user
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-your-openai-key", [EnvironmentVariableTarget]::User)
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-your-anthropic-key", [EnvironmentVariableTarget]::User)
```

#### Method 3: Configuration File
```powershell
# Create configuration directory
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.ai\gsai"

# Edit configuration file
notepad "$env:USERPROFILE\.ai\gsai\.env"
```

Add to the file:
```env
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-your-anthropic-key
APPROVAL_MODE=auto-edit
WEB_SEARCH_ENABLED=true
```

## 🔄 Updating

### Manual Update
```powershell
# Download new version
Invoke-WebRequest -Uri "https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-windows-x86_64.exe" -OutFile "$env:TEMP\gsai-new.exe"

# Replace existing (may need to stop any running gsai processes)
Stop-Process -Name "gsai" -Force -ErrorAction SilentlyContinue
Move-Item "$env:TEMP\gsai-new.exe" "C:\Program Files\GitStart\gsai.exe" -Force
```

### Package Manager Updates
```powershell
# Winget
winget upgrade GitStart.CoPilotCLI

# Chocolatey
choco upgrade gsai

# Scoop
scoop update gsai
```

### From Source
```powershell
cd gitstart-cli
git pull origin main
uv tool install . --force
```

## 🗑️ Uninstallation

### Remove Manual Installation
```powershell
# Remove executable
Remove-Item "C:\Program Files\GitStart\gsai.exe" -Force

# Remove directory if empty
Remove-Item "C:\Program Files\GitStart" -Force

# Remove from PATH
$newPath = ($env:PATH.Split(';') | Where-Object { $_ -ne "C:\Program Files\GitStart" }) -join ';'
[Environment]::SetEnvironmentVariable("PATH", $newPath, [EnvironmentVariableTarget]::Machine)

# Remove configuration
Remove-Item "$env:USERPROFILE\.ai\gsai" -Recurse -Force
```

### Remove Package Manager Installations
```powershell
# Winget
winget uninstall GitStart.CoPilotCLI

# Chocolatey
choco uninstall gsai

# Scoop
scoop uninstall gsai

# uv tool
uv tool uninstall gsai
```

## 🐛 Windows-Specific Troubleshooting

### Common Issues

#### "gsai is not recognized as an internal or external command"

**Check if gsai.exe exists:**
```powershell
Get-Command gsai -ErrorAction SilentlyContinue
```

**Fix PATH issues:**
```powershell
# Check current PATH
$env:PATH.Split(';') | Where-Object { $_ -like "*GitStart*" }

# Add to PATH for current session
$env:PATH += ";C:\Program Files\GitStart"

# Make permanent
[Environment]::SetEnvironmentVariable("PATH", "$env:PATH;C:\Program Files\GitStart", [EnvironmentVariableTarget]::User)
```

#### "Access is denied" or Permission Issues

**Run as Administrator:**
```powershell
# Start PowerShell as Administrator
Start-Process powershell -Verb RunAs
```

**Fix file permissions:**
```powershell
# Take ownership
takeown /f "C:\Program Files\GitStart\gsai.exe"

# Grant permissions
icacls "C:\Program Files\GitStart\gsai.exe" /grant Everyone:F
```

#### Windows Defender Blocking Execution

**Add exclusion via PowerShell:**
```powershell
# Run as Administrator
Add-MpPreference -ExclusionPath "C:\Program Files\GitStart"
Add-MpPreference -ExclusionProcess "gsai.exe"
```

#### SSL Certificate Issues

**Update certificates:**
```powershell
# Update Windows certificates
certlm.msc  # Open Certificate Manager

# Or use PowerShell
Import-Module PKI
Update-CARootCertificate
```

#### Python/uv Installation Issues

**Fix Python installation:**
```powershell
# Repair Python installation
python -m pip install --upgrade pip setuptools

# Reinstall uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Performance Issues

#### Slow startup
```powershell
# Disable Windows Defender real-time scanning for gsai
Add-MpPreference -ExclusionProcess "gsai.exe"

# Or exclude the entire directory
Add-MpPreference -ExclusionPath "C:\Program Files\GitStart"
```

#### High memory usage
```powershell
# Check system resources
Get-Process gsai
Get-WmiObject -Class Win32_ComputerSystem | Select-Object TotalPhysicalMemory

# Close other applications if needed
```

## 🎨 Windows Integration

### Windows Terminal Integration

Create a Windows Terminal profile:

1. Open Windows Terminal settings
2. Add new profile:
```json
{
    "commandline": "gsai chat",
    "name": "GitStart CoPilot",
    "icon": "path/to/icon.ico",
    "startingDirectory": "%USERPROFILE%"
}
```

### Desktop Shortcut

```powershell
# Create desktop shortcut
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\GitStart CoPilot.lnk")
$Shortcut.TargetPath = "C:\Program Files\GitStart\gsai.exe"
$Shortcut.Arguments = "chat"
$Shortcut.WorkingDirectory = "$env:USERPROFILE"
$Shortcut.Save()
```

### File Association

Register `.gsai` files (if needed):

```powershell
# Associate .gsai files with gsai
cmd /c 'assoc .gsai=gsaifile'
cmd /c 'ftype gsaifile="C:\Program Files\GitStart\gsai.exe" "%1"'
```

## 📞 Getting Help

### Windows-Specific Support

1. **Check Windows Event Viewer:**
   ```powershell
   # Open Event Viewer
   eventvwr.msc
   ```

2. **PowerShell Diagnostics:**
   ```powershell
   # Check .NET version
   Get-ItemProperty "HKLM:SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full\" -Name Release

   # Check PowerShell version
   $PSVersionTable.PSVersion
   ```

3. **System Information:**
   ```powershell
   # Get system info
   Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, TotalPhysicalMemory
   ```

### Common Locations

- **Executable**: `C:\Program Files\GitStart\gsai.exe`
- **Configuration**: `%USERPROFILE%\.ai\gsai\.env`
- **Temp files**: `%TEMP%`
- **User PATH**: `HKCU:\Environment`
- **System PATH**: `HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment`

---

**Next:** [Quick Start Guide](quick-start.md) | **See also:** [Configuration Guide](configuration.md)