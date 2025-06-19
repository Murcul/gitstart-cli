# Private Repository Public Release Guide

Complete guide for distributing GitStart CoPilot CLI from a private repository with public installation URLs.

## 🎯 How It Works

**The Solution**: Even though your repository is private, GitHub releases and their assets can be made publicly accessible. This allows you to:

✅ Keep source code private  
✅ Make installers publicly downloadable  
✅ Provide one-command installation  
✅ Distribute without exposing repository access  

## 🚀 Creating a Public Release

### Step 1: Set Up GitHub Secrets

In your private repository, add these secrets:
1. Go to **Settings** → **Secrets and Variables** → **Actions**
2. Add these repository secrets:
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `ANTHROPIC_API_KEY` - Your Anthropic API key

### Step 2: Create Release

Use the trigger script to create a release:

```bash
# Create and push a release tag (triggers automatic build)
./trigger-release.sh tag-release v1.0.0

# Or trigger manual build
./trigger-release.sh manual-build v1.0.0
```

### Step 3: Public URLs Available

After the workflow completes, these URLs become publicly accessible:

**Installation Commands (work for anyone):**
```bash
# Windows
iwr -useb https://github.com/Murcul/gitstart-cli/releases/download/v1.0.0/install.ps1 | iex

# Linux/macOS
curl -sSL https://github.com/Murcul/gitstart-cli/releases/download/v1.0.0/install.sh | bash

# Zero-dependency
curl -sSL https://github.com/Murcul/gitstart-cli/releases/download/v1.0.0/standalone-install.sh | bash
```

**Direct Downloads (work for anyone):**
- Windows: `https://github.com/Murcul/gitstart-cli/releases/download/v1.0.0/gsai-v1.0.0-windows-x86_64.zip`
- macOS: `https://github.com/Murcul/gitstart-cli/releases/download/v1.0.0/gsai-v1.0.0-macos-x86_64.zip`
- Linux: `https://github.com/Murcul/gitstart-cli/releases/download/v1.0.0/gsai-v1.0.0-linux-x86_64.zip`

## 📦 What Gets Created

### Public Assets (accessible to anyone)
- ✅ **Cross-platform executables** (Windows .exe, macOS, Linux)
- ✅ **Installation scripts** (install.ps1, install.sh, standalone-install.sh)
- ✅ **Source packages** (complete source, minimal, installers-only)
- ✅ **Documentation** (installation guides, release notes)
- ✅ **Public installation guide** (step-by-step instructions)

### Private Assets (repository access required)
- 🔒 **Source code** (remains private in repository)
- 🔒 **Development files** (tests, configuration, etc.)
- 🔒 **GitHub repository** (private, invite-only access)

## 🔧 GitHub Actions Workflow Features

The updated workflow (`build-release.yml`) includes:

### Enhanced Build Process
1. **Multi-platform builds** (Windows, macOS, Linux)
2. **API key embedding** from GitHub Secrets
3. **PyInstaller executable creation** with dependencies
4. **ZIP packaging** with installation instructions
5. **Source code packaging** for developers

### Public Release Creation
1. **Public asset upload** to GitHub releases
2. **Installation script generation** with correct URLs
3. **Comprehensive release notes** with download links
4. **Public installation guide** creation
5. **Direct download URLs** that work publicly

### Smart Distribution
1. **Latest release URLs** for always-current installs
2. **Version-specific URLs** for pinned installations
3. **Platform detection** in installation scripts
4. **Fallback strategies** for restricted environments

## 🌍 Distribution Strategy

### For End Users
Share these simple commands:

```bash
# Latest version install
curl -sSL https://github.com/Murcul/gitstart-cli/releases/latest/download/install.sh | bash

# Specific version install
curl -sSL https://github.com/Murcul/gitstart-cli/releases/download/v1.0.0/install.sh | bash
```

### For Documentation/Websites
Include in your documentation:

```markdown
## Installation

### Windows
```powershell
iwr -useb https://github.com/Murcul/gitstart-cli/releases/latest/download/install.ps1 | iex
```

### Linux/macOS
```bash
curl -sSL https://github.com/Murcul/gitstart-cli/releases/latest/download/install.sh | bash
```
```

### For Enterprise/Internal
- Share the `PUBLIC-INSTALL.md` guide
- Use version-pinned URLs for stability
- Set up internal mirrors if needed

## 🔐 Security Considerations

### What's Public
✅ **Compiled executables** - Safe, no source code exposed  
✅ **Installation scripts** - Standard deployment tools  
✅ **Documentation** - Usage and installation guides  
✅ **Release notes** - Feature and change information  

### What Stays Private
🔒 **Source code** - Never exposed in releases  
🔒 **Development secrets** - Only in GitHub Secrets  
🔒 **Internal documentation** - Repository access required  
🔒 **Development workflow** - Private repository only  

### API Key Embedding
- ✅ **Secure embedding** - Keys compiled into executable
- ✅ **No plain text exposure** - Keys not visible in releases
- ✅ **Rotation capability** - New releases can embed new keys
- ✅ **User override** - Users can still set their own keys

## 📊 Usage Analytics

### Track Distribution
Monitor release downloads in GitHub:
1. Go to **Releases** in your repository
2. View download counts for each asset
3. Track which platforms are most popular
4. Monitor adoption of new versions

### Monitor Installation
Add analytics to your application:
```bash
# Track successful installations
gsai status --report-install
```

## 🚨 Emergency Procedures

### Revoke Release
If you need to remove a public release:
```bash
# Delete specific release
gh release delete v1.0.0 --yes

# Delete tag
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0
```

### Update Keys
To update embedded API keys:
1. Update GitHub Secrets
2. Create new release
3. Notify users to update

### Force New Version
To force users to specific version:
```bash
# Create new release with important updates
./trigger-release.sh tag-release v1.0.1

# Update documentation to point to new version
```

## 🎉 Success Verification

After creating a release, verify public access:

### Test Installation URLs
```bash
# Test without repository access (use incognito/private browser)
curl -I https://github.com/Murcul/gitstart-cli/releases/latest/download/install.sh
# Should return 200 OK

# Test direct download
curl -I https://github.com/Murcul/gitstart-cli/releases/latest/download/gsai-latest-linux-x86_64.zip
# Should return 200 OK
```

### Verify Installation
```bash
# Install and test
curl -sSL https://github.com/Murcul/gitstart-cli/releases/latest/download/install.sh | bash
gsai --version
gsai status
```

## 📈 Scaling Distribution

### CDN Integration
For high-volume distribution:
```bash
# Mirror releases to CDN
aws s3 sync releases/ s3://your-cdn-bucket/gsai/
```

### Package Managers
Consider submitting to package managers:
```bash
# Homebrew (macOS)
# Chocolatey (Windows)
# APT/YUM repositories (Linux)
```

---

**Result**: Your private repository now provides public, one-command installation while keeping all source code completely private!

## 🔗 Quick Links

- **Trigger Release**: `./trigger-release.sh tag-release v1.0.0`
- **View Releases**: https://github.com/Murcul/gitstart-cli/releases
- **Public Install Guide**: `PUBLIC-INSTALL.md`
- **Monitor Builds**: `gh run list --workflow=build-release.yml`