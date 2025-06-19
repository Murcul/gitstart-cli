# Immediate Fix for Release v0.0.7

## 🚨 Quick Resolution

The workflow is still failing because the cleanup isn't working properly in the GitHub Actions environment. Here's how to fix it immediately:

### Step 1: Manual Cleanup

Run these commands locally to clean up the problematic release:

```bash
# Clean up v0.0.7 manually
./trigger-release.sh clean-release v0.0.7

# If that doesn't work, try manual commands:
gh release delete v0.0.7 --yes
git tag -d v0.0.7
git push origin :refs/tags/v0.0.7
```

### Step 2: Create a New Version

Use a fresh version number to avoid conflicts:

```bash
# Use v0.0.8 instead
./trigger-release.sh tag-release v0.0.8
```

### Step 3: Alternative - Manual Release Creation

If the automated workflow keeps failing, create the release manually:

```bash
# 1. Create and push the tag manually
git tag v0.0.8
git push origin v0.0.8

# 2. Let GitHub Actions build the artifacts
# (The build jobs should work, only the release creation is failing)

# 3. After the build completes, create the release manually
gh release create v0.0.8 \
  --title "GitStart CoPilot CLI v0.0.8" \
  --notes "Cross-platform AI coding assistant with embedded API keys" \
  --prerelease=false
```

### Step 4: Upload Artifacts Manually (if needed)

If you need to upload the built artifacts manually:

```bash
# Download artifacts from the failed workflow run
gh run download [RUN_ID]

# Upload to the release
gh release upload v0.0.8 \
  gsai-v0.0.8-windows-x86_64.zip \
  gsai-v0.0.8-macos-x86_64.zip \
  gsai-v0.0.8-linux-x86_64.zip \
  install.sh \
  install.ps1 \
  standalone-install.sh
```

## 🔧 Root Cause Analysis

The issue is likely one of these:

1. **Permission Issue**: GitHub Actions might not have write permissions to delete releases
2. **Timing Issue**: The tag cleanup isn't completing before the release creation
3. **API Rate Limiting**: Too many API calls in quick succession

## 🛠️ Permanent Fix Options

### Option 1: Simplify Workflow (Recommended)

Remove the automatic cleanup and use unique version numbers:

```bash
# Always increment version numbers instead of reusing
./trigger-release.sh tag-release v0.0.8
./trigger-release.sh tag-release v0.0.9
# etc.
```

### Option 2: Add Workflow Permissions

Add explicit permissions to the workflow:

```yaml
permissions:
  contents: write
  packages: write
  actions: read
  security-events: write
```

### Option 3: Use GitHub CLI in Workflow

Ensure the workflow has access to `gh` CLI:

```bash
# Add to workflow
- name: Setup GitHub CLI
  run: |
    type -p curl >/dev/null || sudo apt update && sudo apt install curl -y
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    sudo apt update && sudo apt install gh -y
```

## ✅ Immediate Action Plan

**Right now, do this:**

```bash
# 1. Clean up the problematic version
./trigger-release.sh clean-release v0.0.7

# 2. Use a new version number
./trigger-release.sh tag-release v0.0.8

# 3. Monitor the workflow
gh run watch
```

**If it still fails:**

```bash
# Use manual approach
git tag v0.0.9
git push origin v0.0.9
# Then create release via GitHub web interface after artifacts build
```

## 🎯 Success Indicators

After a successful release, you should be able to run:

```bash
# Test the public installation URLs
curl -I https://github.com/Murcul/gitstart-cli/releases/download/v0.0.8/install.sh
# Should return: HTTP/2 200

curl -I https://github.com/Murcul/gitstart-cli/releases/download/v0.0.8/install.ps1  
# Should return: HTTP/2 200
```

---

**Try the immediate fix with v0.0.8 - the workflow improvements should handle the cleanup better now!**