# Release Issue Resolution Guide

Quick guide to fix the GitHub Actions release issues you encountered.

## 🐛 Issues Fixed

### 1. Invalid `make_latest` Parameter
**Error**: `Warning: Unexpected input(s) 'make_latest'`

**Fix**: Removed the invalid `make_latest` parameter from the release action.

### 2. Release Already Exists Error  
**Error**: `[{"resource":"Release","code":"already_exists","field":"tag_name"}]`

**Fix**: Added automatic cleanup of existing releases and tags before creating new ones.

## 🚀 Resolution Commands

### Option 1: Clean and Retry (Recommended)

```bash
# Clean up the existing release first
./trigger-release.sh clean-release v0.0.6

# Then create a new release
./trigger-release.sh tag-release v0.0.6
```

### Option 2: Use a New Version

```bash
# Create a new version to avoid conflicts
./trigger-release.sh tag-release v0.0.7
```

### Option 3: Manual Cleanup

```bash
# Delete release manually
gh release delete v0.0.6 --yes

# Delete tag manually  
git tag -d v0.0.6
git push origin :refs/tags/v0.0.6

# Then retry
./trigger-release.sh tag-release v0.0.6
```

## 🔧 What's Fixed in the Workflow

### Automatic Cleanup
The workflow now automatically:
1. **Deletes existing releases** if they exist
2. **Removes existing tags** if they exist  
3. **Creates fresh releases** without conflicts

### Enhanced Error Handling
```yaml
- name: Delete existing release if it exists
  run: |
    # Delete existing release and tag if they exist
    if gh release view ${{ env.VERSION }} >/dev/null 2>&1; then
      echo "Deleting existing release ${{ env.VERSION }}"
      gh release delete ${{ env.VERSION }} --yes
    fi
```

### Corrected File Paths
- Fixed installer script copying paths
- Corrected repository URLs throughout
- Fixed heredoc delimiters for YAML compatibility

## 🎯 New Features Added

### Clean Release Command
```bash
# New command to clean up releases
./trigger-release.sh clean-release v0.0.6
```

### Better Error Recovery
- Automatic retry mechanisms
- Cleaner error messages
- Step-by-step resolution guidance

## ✅ Next Steps

1. **Clean the existing release**:
   ```bash
   ./trigger-release.sh clean-release v0.0.6
   ```

2. **Create a new release**:
   ```bash
   ./trigger-release.sh tag-release v0.0.6
   ```

3. **Monitor the build**:
   ```bash
   gh run watch
   ```

4. **Verify public URLs work**:
   ```bash
   # After successful build, test these URLs:
   curl -I https://github.com/Murcul/gitstart-cli/releases/download/v0.0.6/install.sh
   ```

## 🔄 If Issues Persist

### Check Permissions
```bash
# Ensure you have the right permissions
gh auth status
gh repo view Murcul/gitstart-cli
```

### Verify Secrets
1. Go to **Settings** → **Secrets and Variables** → **Actions**
2. Ensure these secrets exist:
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`

### Manual Trigger
```bash
# If automation fails, trigger manually
gh workflow run build-release.yml --field version=v0.0.6 --field make_public=true
```

## 📊 Success Indicators

After a successful release, you should see:

✅ **Public installation URLs work**:
```bash
curl -sSL https://github.com/Murcul/gitstart-cli/releases/download/v0.0.6/install.sh | bash
```

✅ **Assets are publicly downloadable**:
- Windows: `gsai-v0.0.6-windows-x86_64.zip`
- macOS: `gsai-v0.0.6-macos-x86_64.zip`  
- Linux: `gsai-v0.0.6-linux-x86_64.zip`

✅ **Installation works without repository access**

---

**The workflow is now fixed and ready to create clean, public releases from your private repository!**