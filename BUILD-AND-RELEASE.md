# GitStart CoPilot CLI - Build and Release Guide

Complete guide for building and releasing GitStart CoPilot CLI with embedded API keys.

## 🚀 Quick Commands

### Trigger a Release Build

```bash
# Create a new release (automatic GitHub Actions build)
./trigger-release.sh tag-release v1.0.0

# Manual build without creating a tag
./trigger-release.sh manual-build v1.0.0-beta

# Check build status
./trigger-release.sh check-status
```

### One-Line Release Command

```bash
# Create and release v1.0.0 with embedded API keys
./trigger-release.sh tag-release v1.0.0
```

## 📦 What Gets Built

When you trigger a release, GitHub Actions automatically creates:

### 🎯 Standalone Executables
- **Windows**: `gsai-v1.0.0-windows-x86_64.zip`
- **macOS**: `gsai-v1.0.0-macos-x86_64.zip`  
- **Linux**: `gsai-v1.0.0-linux-x86_64.zip`

Each ZIP contains:
- Standalone executable (no Python required)
- Installation instructions
- Embedded API keys from GitHub Secrets
- Ready to use immediately

### 📋 Source Packages
- **Complete Source**: `gsai-v1.0.0-source.zip` - Full source + installers
- **Minimal Source**: `gsai-v1.0.0-minimal-source.zip` - Python code only
- **Installers Only**: `gsai-v1.0.0-installers.zip` - One-command installers

### 🔧 Installation Scripts
All builds include the one-command installers:
- `install.sh` - Linux/macOS full installer
- `install.ps1` - Windows PowerShell installer
- `standalone-install.sh` - Zero-dependency installer

## 🔑 API Keys Integration

The build system automatically embeds API keys from GitHub Secrets:

### GitHub Secrets Required
Set these in your repository settings:
- `OPENAI_API_KEY` - Your OpenAI API key
- `ANTHROPIC_API_KEY` - Your Anthropic API key

### How It Works
1. GitHub Actions reads API keys from secrets
2. Creates `gsai/build_config.py` with embedded keys
3. Modifies `gsai/config.py` to use embedded keys as defaults
4. Builds executable with keys included
5. Users can use immediately without configuration

## 🛠️ Build Process Details

### Automatic Trigger (Recommended)
```bash
# Creates tag and triggers build
./trigger-release.sh tag-release v1.0.0
```

This will:
1. ✅ Create and push git tag
2. ✅ Trigger GitHub Actions workflow
3. ✅ Build cross-platform executables
4. ✅ Create ZIP packages
5. ✅ Generate source packages
6. ✅ Create GitHub release
7. ✅ Upload all artifacts

### Manual Trigger
```bash
# Build without creating tag
./trigger-release.sh manual-build v1.0.0-test
```

### Using GitHub CLI Directly
```bash
# Trigger build manually
gh workflow run build-release.yml --field version=v1.0.0

# Monitor progress
gh run watch
```

### Using GitHub Web Interface
1. Go to Actions tab in GitHub
2. Select "Build and Release Cross-Platform Executables"
3. Click "Run workflow"
4. Enter version number
5. Click "Run workflow"

## 📊 Monitoring Builds

### Check Status
```bash
./trigger-release.sh check-status
```

### Watch Live Progress
```bash
gh run watch
```

### View Specific Run
```bash
gh run view [RUN_ID]
```

### List Recent Releases
```bash
./trigger-release.sh list-releases
```

## 📁 Build Artifacts

After successful build, you'll have:

```
Release Artifacts:
├── gsai-v1.0.0-windows-x86_64.zip      # Windows executable
├── gsai-v1.0.0-macos-x86_64.zip        # macOS executable  
├── gsai-v1.0.0-linux-x86_64.zip        # Linux executable
├── gsai-v1.0.0-source.zip              # Complete source
├── gsai-v1.0.0-minimal-source.zip      # Python code only
└── gsai-v1.0.0-installers.zip          # Installers only
```

Each executable ZIP contains:
```
gsai-v1.0.0-platform/
├── gsai[.exe]           # Executable
├── README.txt           # Build info
└── INSTALL.txt          # Usage instructions
```

## 🎯 Distribution Commands

After building, share these commands with users:

### Immediate Use (Download Executable)
```bash
# Users download ZIP and run directly
unzip gsai-v1.0.0-linux-x86_64.zip
cd gsai-v1.0.0-linux-x86_64
./gsai chat
```

### One-Command Installation
```bash
# Linux/macOS
curl -sSL https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.sh | bash

# Windows
iwr -useb https://raw.githubusercontent.com/your-org/gitstart-cli/main/install.ps1 | iex
```

### From Source (Developers)
```bash
# Download source ZIP, then:
uv sync && uv run gsai chat
```

## 🔧 Local Testing

### Test Local Build
```bash
# Build locally first
make build-prompt

# Test the executable
./dist/gsai --help
./dist/gsai chat
```

### Test Installation Scripts
```bash
# Test full installer
./install.sh

# Test standalone installer  
./standalone-install.sh
```

## 🐛 Troubleshooting

### Build Fails
1. Check GitHub Actions logs
2. Verify API keys are set in GitHub Secrets
3. Check Python dependencies in `pyproject.toml`
4. Verify PyInstaller configuration in workflow

### Missing Dependencies
```bash
# Update hidden imports in workflow if needed
hiddenimports=[
    'gsai',
    'pydantic_ai',
    'openai',
    'anthropic',
    # Add missing modules here
]
```

### API Key Issues
1. Verify secrets are set: Repository Settings → Secrets and Variables → Actions
2. Check secret names match: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
3. Test keys are valid before building

### Permission Issues
```bash
# Make sure you have access to:
gh auth status
gh repo view
```

## 📚 Related Documentation

- [Installation Guide](docs/installer-guide.md) - Comprehensive installer documentation
- [Running Locally](docs/running-locally.md) - Development and local execution
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions

## 🎉 Success Checklist

After running `./trigger-release.sh tag-release v1.0.0`:

- ✅ GitHub Actions workflow completes successfully
- ✅ All 6 ZIP packages are created
- ✅ GitHub release is published with release notes
- ✅ Executables include embedded API keys
- ✅ Installation instructions are included
- ✅ Users can run immediately without setup

## 🔗 Quick Links

```bash
# View repository
gh repo view

# View actions
gh run list

# View releases  
gh release list

# View latest release
gh release view --web
```

---

**One command builds everything.** The entire cross-platform release with embedded API keys is just:

```bash
./trigger-release.sh tag-release v1.0.0
```