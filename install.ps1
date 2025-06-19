# GitStart CoPilot CLI - Universal Windows Installer
# One-command installation script that handles everything
# Usage: iwr -useb https://raw.githubusercontent.com/Murcul/gitstart-cli/main/install.ps1 | iex

param(
    [string]$InstallDir = "",
    [switch]$Global = $false,
    [switch]$SystemWide = $false
)

# Configuration
$RepoUrl = "https://github.com/Murcul/gitstart-cli"
$ArchiveUrl = "https://github.com/Murcul/gitstart-cli/archive/refs/heads/main.zip"
$TempDir = "$env:TEMP\gsai-install-$(Get-Random)"
$AppName = "gsai"

# Check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Determine installation directory - default to system-wide
if ($InstallDir -eq "") {
    # Try system-wide first (Program Files)
    $InstallDir = "$env:ProgramFiles\GitStart"
    $IsSystemInstall = $true
    
    # If not admin and not explicitly requested user install, try to elevate
    if (-not (Test-Administrator) -and -not $Global -and -not $SystemWide) {
        Write-Host "GitStart CoPilot CLI will be installed system-wide for all users." -ForegroundColor Yellow
        Write-Host "This requires administrator privileges." -ForegroundColor Yellow
        $choice = Read-Host "Install system-wide (requires admin) [Y] or user-only [N]? (Y/n)"
        
        if ($choice -eq "n" -or $choice -eq "N") {
            $InstallDir = "$env:LOCALAPPDATA\GitStart"
            $IsSystemInstall = $false
        }
    }
} else {
    $IsSystemInstall = $InstallDir.StartsWith($env:ProgramFiles)
}

# Request elevation if needed
function Request-Elevation {
    if (-not (Test-Administrator)) {
        Write-ColorOutput "Administrator privileges required for system-wide installation." "Yellow"
        Write-ColorOutput "Attempting to restart with elevation..." "Blue"
        
        # Get the current script content
        $scriptContent = $MyInvocation.MyCommand.Definition
        
        # Create elevated script
        $elevatedScript = @"
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
`$InstallDir = "$InstallDir"
`$IsSystemInstall = `$true
$scriptContent
"@
        
        # Save to temp file
        $tempScript = "$env:TEMP\gsai-install-elevated.ps1"
        $elevatedScript | Out-File -FilePath $tempScript -Encoding UTF8
        
        try {
            # Run elevated
            Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$tempScript`"" -Verb RunAs -Wait
            
            # Clean up
            Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
            
            Write-ColorOutput "Installation completed with elevated privileges." "Green"
            exit 0
        } catch {
            Write-ColorOutput "Failed to elevate privileges. Installing to user directory instead." "Yellow"
            $script:InstallDir = "$env:LOCALAPPDATA\GitStart"
            $script:IsSystemInstall = $false
        }
    }
}

# Colors for output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Step {
    param([string]$Message)
    Write-ColorOutput "[STEP] $Message" "Cyan"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "[SUCCESS] $Message" "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "[WARN] $Message" "Yellow"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "[ERROR] $Message" "Red"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "[INFO] $Message" "Blue"
}

# Print banner
function Show-Banner {
    Write-ColorOutput "" "Blue"
    Write-ColorOutput "╔══════════════════════════════════════════════════════════╗" "Blue"
    Write-ColorOutput "║               GitStart CoPilot CLI Installer             ║" "Blue"
    Write-ColorOutput "║                   Made by GitStart AI 🤖                ║" "Blue"
    Write-ColorOutput "╚══════════════════════════════════════════════════════════╝" "Blue"
    Write-ColorOutput "" "Blue"
    Write-ColorOutput "✨ One-command installation - no manual setup required!" "White"
    Write-ColorOutput "" "Blue"
}

# Cleanup function
function Remove-TempFiles {
    if (Test-Path $TempDir) {
        Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# Detect system
function Get-SystemInfo {
    Write-Step "Detecting system configuration..."
    
    $OS = "windows"
    $Arch = $env:PROCESSOR_ARCHITECTURE.ToLower()
    
    switch ($Arch) {
        "amd64" { $Arch = "x64" }
        "x86" { $Arch = "x86" }
        "arm64" { $Arch = "arm64" }
        default { 
            Write-Error "Unsupported architecture: $Arch"
            exit 1
        }
    }
    
    Write-Success "Detected: $OS-$Arch"
    return @{ OS = $OS; Arch = $Arch }
}

# Check prerequisites
function Test-Prerequisites {
    Write-Step "Checking system prerequisites..."
    
    $missingCommands = @()
    
    # Check for PowerShell 5.1+
    if ($PSVersionTable.PSVersion.Major -lt 5) {
        Write-Error "PowerShell 5.1 or higher is required"
        exit 1
    }
    
    # Check for Python
    try {
        $pythonVersion = & python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python detected: $pythonVersion"
        } else {
            $missingCommands += "python"
        }
    } catch {
        $missingCommands += "python"
    }
    
    # Check for Git
    try {
        $gitVersion = & git --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Git detected: $gitVersion"
        } else {
            $missingCommands += "git"
        }
    } catch {
        Write-Warning "Git not found - will try to install"
        $missingCommands += "git"
    }
    
    if ($missingCommands.Count -gt 0) {
        Install-Prerequisites $missingCommands
    }
}

# Install prerequisites
function Install-Prerequisites {
    param([array]$Commands)
    
    Write-Step "Installing prerequisites..."
    
    # Try to install using package managers
    $hasWinget = Get-Command winget -ErrorAction SilentlyContinue
    $hasChoco = Get-Command choco -ErrorAction SilentlyContinue
    
    foreach ($cmd in $Commands) {
        switch ($cmd) {
            "python" {
                if ($hasWinget) {
                    Write-Info "Installing Python with winget..."
                    winget install Python.Python.3.12 --silent
                } elseif ($hasChoco) {
                    Write-Info "Installing Python with Chocolatey..."
                    choco install python312 -y
                } else {
                    Write-Warning "Please install Python 3.10+ from https://python.org/downloads/"
                    Write-Warning "Make sure to check 'Add Python to PATH' during installation"
                    Read-Host "Press Enter after installing Python"
                }
            }
            "git" {
                if ($hasWinget) {
                    Write-Info "Installing Git with winget..."
                    winget install Git.Git --silent
                } elseif ($hasChoco) {
                    Write-Info "Installing Git with Chocolatey..."
                    choco install git -y
                } else {
                    Write-Warning "Please install Git from https://git-scm.com/download/win"
                    Read-Host "Press Enter after installing Git"
                }
            }
        }
    }
    
    # Refresh PATH
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
    
    Write-Success "Prerequisites installation completed"
}

# Install uv
function Install-Uv {
    Write-Step "Installing uv package manager..."
    
    try {
        $uvVersion = & uv --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "uv already installed: $uvVersion"
            return
        }
    } catch {
        # uv not installed, continue with installation
    }
    
    try {
        Write-Info "Downloading and installing uv..."
        Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
        
        # Add to PATH for current session
        $env:PATH += ";$env:USERPROFILE\.local\bin"
        
        Write-Success "uv installed successfully ✓"
    } catch {
        Write-Error "Failed to install uv: $_"
        exit 1
    }
}

# Download source code
function Get-SourceCode {
    Write-Step "Downloading GitStart CoPilot CLI source code..."
    
    New-Item -ItemType Directory -Path $TempDir -Force | Out-Null
    Set-Location $TempDir
    
    try {
        Write-Info "Downloading source archive..."
        Invoke-WebRequest -Uri $ArchiveUrl -OutFile "source.zip"
        Write-Success "Source code downloaded ✓"
        
        Write-Info "Extracting archive..."
        Expand-Archive -Path "source.zip" -DestinationPath "." -Force
        Write-Success "Source code extracted ✓"
        
        # Find extracted directory
        $extractedDir = Get-ChildItem -Directory | Where-Object { $_.Name -like "gitstart-cli-*" } | Select-Object -First 1
        if ($extractedDir) {
            Set-Location $extractedDir.FullName
            Write-Success "Entered source directory: $($extractedDir.Name)"
        } else {
            Write-Error "Could not find extracted source directory"
            exit 1
        }
    } catch {
        Write-Error "Failed to download/extract source code: $_"
        exit 1
    }
}

# Build application
function Build-Application {
    Write-Step "Building GitStart CoPilot CLI..."
    
    try {
        # Install dependencies
        Write-Info "Installing dependencies..."
        & uv sync
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install dependencies"
        }
        Write-Success "Dependencies installed ✓"
        
        # Try to build executable
        Write-Info "Creating standalone executable..."
        
        # Create build script
        $buildScript = @"
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
    name='gsai.exe',
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
"@
        
        $buildScript | Out-File -FilePath "build_simple.py" -Encoding UTF8
        
        # Try to build
        & uv run python build_simple.py
        
        if (Test-Path "dist\gsai.exe") {
            Write-Success "Executable built successfully ✓"
        } else {
            Write-Warning "PyInstaller build failed, creating wrapper script..."
            New-WrapperScript
        }
    } catch {
        Write-Warning "Build failed, creating wrapper script..."
        New-WrapperScript
    }
}

# Create wrapper script as fallback
function New-WrapperScript {
    Write-Info "Creating wrapper script..."
    
    try {
        # Try uv tool install first
        & uv tool install .
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Installed via uv tool ✓"
            return
        }
    } catch {
        # Continue with manual wrapper
    }
    
    # Create manual wrapper
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    
    $wrapperScript = @"
@echo off
REM GitStart CoPilot CLI Wrapper Script
REM Auto-generated by installer

set "SCRIPT_DIR=%USERPROFILE%\.gsai"
set "VENV_DIR=%SCRIPT_DIR%\venv"

REM Create virtual environment if it doesn't exist
if not exist "%VENV_DIR%" (
    python -m venv "%VENV_DIR%"
    call "%VENV_DIR%\Scripts\activate.bat"
    pip install -e "%SCRIPT_DIR%\source"
) else (
    call "%VENV_DIR%\Scripts\activate.bat"
)

REM Run gsai
python -m gsai %*
"@
    
    $wrapperScript | Out-File -FilePath "$InstallDir\gsai.bat" -Encoding ASCII
    
    # Copy source to permanent location
    $gsaiDir = "$env:USERPROFILE\.gsai"
    New-Item -ItemType Directory -Path $gsaiDir -Force | Out-Null
    Copy-Item -Path "." -Destination "$gsaiDir\source" -Recurse -Force
    
    Write-Success "Wrapper script created ✓"
}

# Install application
function Install-Application {
    Write-Step "Installing GitStart CoPilot CLI..."
    
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    
    if (Test-Path "dist\gsai.exe") {
        Copy-Item -Path "dist\gsai.exe" -Destination "$InstallDir\gsai.exe" -Force
        Write-Success "Executable installed to $InstallDir\gsai.exe ✓"
    } elseif (Test-Path "$InstallDir\gsai.bat") {
        Write-Success "Wrapper script already installed ✓"
    } else {
        Write-Error "No executable or wrapper script found"
        exit 1
    }
}

# Configure PATH
function Set-PathConfiguration {
    Write-Step "Configuring PATH..."
    
    # Determine which PATH scope to use
    $PathScope = if ($IsSystemInstall) { "Machine" } else { "User" }
    
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", $PathScope)
    
    if ($currentPath -like "*$InstallDir*") {
        Write-Success "PATH already configured ✓"
        return
    }
    
    try {
        if ($IsSystemInstall) {
            # System-wide installation - add to Machine PATH
            Write-Info "Adding to system PATH (all users)..."
            if (-not (Test-Administrator)) {
                Write-Warning "Administrator privileges required to modify system PATH"
                Write-Info "Adding to user PATH instead..."
                $PathScope = "User"
                $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
            }
        }
        
        $newPath = "$InstallDir;$currentPath"
        [Environment]::SetEnvironmentVariable("PATH", $newPath, $PathScope)
        
        # Update current session PATH
        $env:PATH = "$InstallDir;$env:PATH"
        
        if ($PathScope -eq "Machine") {
            Write-Success "System PATH configured (all users) ✓"
        } else {
            Write-Success "User PATH configured ✓"
        }
    } catch {
        Write-Error "Failed to configure PATH: $_"
        Write-Warning "Please manually add $InstallDir to your PATH"
        
        if ($IsSystemInstall) {
            Write-Info "To add manually (as Administrator):"
            Write-Info "  setx /M PATH `"$InstallDir;%PATH%`""
        } else {
            Write-Info "To add manually:"
            Write-Info "  setx PATH `"$InstallDir;%PATH%`""
        }
    }
}

# Configure API keys
function Set-ApiKeyConfiguration {
    Write-Step "Setting up configuration..."
    
    $configDir = "$env:USERPROFILE\.ai\gsai"
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    
    $configContent = @"
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
"@
    
    $configContent | Out-File -FilePath "$configDir\.env" -Encoding UTF8
    Write-Success "Configuration template created ✓"
}

# Test installation
function Test-Installation {
    Write-Step "Testing installation..."
    
    try {
        $version = & gsai --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Installation test passed ✓"
            return $true
        } else {
            Write-Warning "gsai command found but failed to run"
            return $false
        }
    } catch {
        Write-Warning "gsai command not found in PATH"
        Write-Info "You may need to restart your terminal or add $InstallDir to PATH"
        return $false
    }
}

# Show completion message
function Show-Completion {
    Write-ColorOutput "" "Green"
    Write-ColorOutput "╔══════════════════════════════════════════════════════════╗" "Green"
    Write-ColorOutput "║                 🎉 Installation Complete! 🎉             ║" "Green"
    Write-ColorOutput "╚══════════════════════════════════════════════════════════╝" "Green"
    Write-ColorOutput "" "Green"
    Write-ColorOutput "GitStart CoPilot CLI has been successfully installed!" "White"
    Write-ColorOutput "" "Green"
    Write-ColorOutput "Quick Start:" "Cyan"
    Write-ColorOutput "  1. Restart your terminal or refresh PATH" "Yellow"
    Write-ColorOutput "  2. Configure your API keys: gsai configure" "Yellow"
    Write-ColorOutput "  3. Start coding with AI: gsai chat" "Yellow"
    Write-ColorOutput "" "Green"
    Write-ColorOutput "Commands:" "Cyan"
    Write-ColorOutput "  gsai --help        - Show help" "White"
    Write-ColorOutput "  gsai configure     - Set up API keys" "White"
    Write-ColorOutput "  gsai status        - Check configuration" "White"
    Write-ColorOutput "  gsai chat          - Start AI coding session" "White"
    Write-ColorOutput "" "Green"
    Write-ColorOutput "Configuration:" "Cyan"
    Write-ColorOutput "  Config file: $env:USERPROFILE\.ai\gsai\.env" "White"
    Write-ColorOutput "  Install location: $InstallDir" "White"
    Write-ColorOutput "" "Green"
    Write-ColorOutput "Get API keys:" "Blue"
    Write-ColorOutput "  OpenAI: https://platform.openai.com/api-keys" "White"
    Write-ColorOutput "  Anthropic: https://console.anthropic.com/" "White"
    Write-ColorOutput "" "Green"
    Write-ColorOutput "Need help? Check the documentation or visit:" "Magenta"
    Write-ColorOutput "  https://github.com/your-org/gitstart-cli" "White"
    Write-ColorOutput "" "Green"
}

# Main installation function
function Start-Installation {
    try {
        Show-Banner
        
        # Check if elevation is needed for system install
        if ($IsSystemInstall -and -not (Test-Administrator)) {
            Request-Elevation
        }
        
        $systemInfo = Get-SystemInfo
        Test-Prerequisites
        Install-Uv
        Get-SourceCode
        Build-Application
        Install-Application
        Set-PathConfiguration
        Set-ApiKeyConfiguration
        
        if (Test-Installation) {
            Show-Completion
        } else {
            Show-Completion
            Write-ColorOutput "Note: You may need to restart your terminal for the PATH changes to take effect." "Yellow"
        }
    } catch {
        Write-Error "Installation failed: $_"
        exit 1
    } finally {
        Remove-TempFiles
    }
}

# Run installation
Start-Installation
