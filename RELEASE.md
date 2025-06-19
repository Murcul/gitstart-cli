# GitStart CoPilot CLI - Release Documentation

This document explains how to build and release cross-platform executables using GitHub Actions.

## 🚀 Automated Release Process

### Creating a Release

#### Method 1: Tag-based Release (Recommended)

```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0
```

This automatically triggers the build workflow and creates a GitHub release with executables for:
- **Windows**: `gsai-v1.0.0-windows-x86_64.exe`
- **macOS**: `gsai-v1.0.0-macos-x86_64`
- **Linux**: `gsai-v1.0.0-linux-x86_64`

#### Method 2: Manual Release

1. Go to your repository on GitHub
2. Navigate to **Actions** → **Build and Release Cross-Platform Executables**
3. Click **Run workflow**
4. Fill in the required information:
   - **Version**: e.g., `v1.0.0`
   - **OpenAI API Key**: (optional) Your OpenAI API key to embed
   - **Anthropic API Key**: (optional) Your Anthropic API key to embed
5. Click **Run workflow**

### API Key Configuration

#### Option 1: Repository Secrets (Recommended for Private Repos)

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add secrets:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ANTHROPIC_API_KEY`: Your Anthropic API key

These keys will be automatically embedded in all releases.

#### Option 2: Manual Input (Public Repos)

When manually triggering the workflow, you can input API keys directly. **Warning**: These keys will be visible in the workflow logs.

#### Option 3: No Embedded Keys

Leave the API key fields empty. Users will need to configure their own keys using `gsai configure`.

## 🔧 Testing Builds

### Test Build Workflow

Before creating a release, you can test the build process:

1. Go to **Actions** → **Test Build**
2. Click **Run workflow**
3. Select the platform to test
4. Optionally provide test API keys
5. Review the build artifacts

### Local Testing

```bash
# Test the build locally
./build-local.sh

# Test the executable
./dist/gsai --help
./dist/gsai status
```

## 📦 Release Artifacts

Each release includes:

### Executables
- `gsai-{version}-windows-x86_64.exe` - Windows executable
- `gsai-{version}-macos-x86_64` - macOS executable
- `gsai-{version}-linux-x86_64` - Linux executable

### Info Files
- `{executable}.info` - Build information for each platform

### Features
- ✅ Self-contained (no dependencies required)
- ✅ Cross-platform compatibility
- ✅ Embedded API keys (if configured)
- ✅ No Python installation required
- ✅ Single-file distribution

## 🎯 Usage for End Users

### Download and Run

1. **Download** the appropriate executable from the [Releases page](../../releases)
2. **Make executable** (Linux/macOS only):
   ```bash
   chmod +x gsai-*
   ```
3. **Run**:
   ```bash
   ./gsai-* --help
   ```

### First Time Setup

If API keys are not embedded:
```bash
./gsai-* configure
```

### Start Coding

```bash
cd your-project
./gsai-* chat
```

## 🛠️ Build Configuration

### PyInstaller Configuration

The build uses a comprehensive PyInstaller configuration (`gsai.spec`) that includes:

- All gsai modules and dependencies
- Template files and static assets
- Comprehensive hidden imports
- Optimized exclusions for smaller executables
- Cross-platform compatibility

### Build Process

1. **Environment Setup**: Python 3.12, uv, platform-specific tools
2. **Dependency Installation**: All required packages
3. **API Key Embedding**: Creates build-time configuration
4. **Config Modification**: Temporarily modifies config to use embedded keys
5. **PyInstaller Build**: Creates self-contained executable
6. **Testing**: Verifies executable functionality
7. **Artifact Creation**: Prepares release files
8. **Cleanup**: Restores original files

### Build Matrix

| Platform | OS | Architecture | Extension |
|----------|----|-----------| ----------|
| Linux | ubuntu-latest | x86_64 | (none) |
| Windows | windows-latest | x86_64 | .exe |
| macOS | macos-latest | x86_64 | (none) |

## 🔐 Security Considerations

### API Key Security

- **Repository Secrets**: Most secure for private repositories
- **Manual Input**: Use only for testing or one-time builds
- **No Embedded Keys**: Most secure option, requires user configuration

### Binary Distribution

- Executables contain embedded API keys (if configured)
- Treat release binaries as sensitive material
- Consider key rotation strategies
- Use for trusted distribution only

### Recommendations

1. **Private repos**: Use repository secrets
2. **Public repos**: Don't embed API keys, let users configure their own
3. **Team distribution**: Use repository secrets with team access control
4. **Personal use**: Any method is acceptable

## 🚨 Troubleshooting

### Build Failures

1. **Check workflow logs** in the Actions tab
2. **Verify Python 3.12** compatibility of dependencies
3. **Test locally** using `./build-local.sh`
4. **Check hidden imports** in `gsai.spec` if modules are missing

### Runtime Issues

1. **Test basic commands**: `--help`, `--version`, `status`
2. **Check API key configuration**: Use `status` command
3. **Verify platform compatibility**: Ensure correct executable for your OS
4. **File permissions**: Make sure executable bit is set (Linux/macOS)

### Common Issues

**"Permission denied"** (Linux/macOS):
```bash
chmod +x gsai-*
```

**"Module not found"** errors:
- Add missing modules to `hiddenimports` in `gsai.spec`
- Test local build first

**API key issues**:
```bash
./gsai-* configure
```

## 📝 Version Management

### Semantic Versioning

Use semantic versioning for tags:
- `v1.0.0` - Major release
- `v1.1.0` - Minor release (new features)
- `v1.1.1` - Patch release (bug fixes)
- `v1.0.0-beta.1` - Pre-release (marked as prerelease)

### Release Notes

The workflow automatically generates release notes including:
- Download links for all platforms
- Usage instructions
- Build information
- Feature highlights

## 🎉 Complete Workflow

1. **Develop** your changes
2. **Test locally**: `./build-local.sh`
3. **Commit and push** changes
4. **Create tag**: `git tag v1.0.0 && git push origin v1.0.0`
5. **Monitor build** in Actions tab
6. **Verify release** in Releases page
7. **Download and test** executables
8. **Share** with users

The automated system handles everything from building to publishing, creating a seamless release experience for both developers and end users.