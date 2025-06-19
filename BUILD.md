# Building GitStart CoPilot CLI Executable

This document provides instructions for building a standalone, shareable executable of the GitStart CoPilot CLI with embedded API keys.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Git
- At least one API key (OpenAI or Anthropic)

## Quick Start

### Option 1: Using Makefile (Recommended)

```bash
# Install dependencies
make install

# Build with interactive API key prompts
make build-prompt

# Or build with environment variables
OPENAI_API_KEY="sk-your-key" ANTHROPIC_API_KEY="sk-your-key" make build
```

### Option 2: Using the Build Script Directly

```bash
# Install dependencies
uv sync --dev

# Build with API keys
python build_executable.py \
  --openai-key "sk-your-openai-key" \
  --anthropic-key "sk-your-anthropic-key"
```

## Build Options

### Environment Variables

Set API keys as environment variables:

```bash
export OPENAI_API_KEY="sk-your-openai-key-here"
export ANTHROPIC_API_KEY="sk-your-anthropic-key-here"
make build
```

### Interactive Build

For secure key entry without exposing them in shell history:

```bash
make build-prompt
```

### Command Line Arguments

```bash
python build_executable.py \
  --openai-key "sk-..." \
  --anthropic-key "sk-..." \
  --output-dir ./dist \
  --app-name gsai
```

## Build Script Options

| Option | Default | Description |
|--------|---------|-------------|
| `--openai-key` | None | OpenAI API key to embed |
| `--anthropic-key` | None | Anthropic API key to embed |
| `--output-dir` | `dist` | Output directory for executable |
| `--app-name` | `gsai` | Name of the executable file |

## Available Make Targets

| Target | Description |
|--------|-------------|
| `make install` | Install project dependencies |
| `make dev-install` | Install development dependencies |
| `make build` | Build executable (requires env vars) |
| `make build-prompt` | Build with interactive key prompts |
| `make build-test` | Build without embedded keys (for testing) |
| `make clean` | Clean all build artifacts |
| `make test` | Run test suite |
| `make lint` | Run code formatting and linting |
| `make typecheck` | Run type checking with mypy |
| `make quality` | Run all quality checks |
| `make release` | Build release version with all checks |

## Build Process

The build process performs the following steps:

1. **Dependency Installation**: Installs PyInstaller and other build dependencies
2. **Key Embedding**: Creates a temporary build configuration with API keys
3. **Config Modification**: Temporarily modifies the config to use embedded keys
4. **Executable Creation**: Uses PyInstaller to create a standalone executable
5. **Cleanup**: Restores original files and removes temporary build artifacts

## Output

After a successful build, you'll find:

- `dist/gsai` - The standalone executable
- Build logs showing the process status

## Testing the Executable

```bash
# Test basic functionality
./dist/gsai --help

# Test with a simple command
./dist/gsai version

# Test configuration status
./dist/gsai status
```

## Security Considerations

### API Key Protection

- API keys are embedded directly into the executable binary
- Use this only for personal use or trusted distribution
- Consider the security implications of distributing API keys

### Best Practices

1. **Personal Use**: Best for creating executables for your own use
2. **Team Distribution**: Only share with trusted team members
3. **Key Rotation**: Regularly rotate embedded API keys
4. **Binary Protection**: Treat the executable as sensitive material

## Troubleshooting

### Common Build Issues

**Missing Dependencies**
```bash
# Install uv if not available
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install development dependencies
make dev-install
```

**PyInstaller Issues**
```bash
# Clean and rebuild
make clean
make build-prompt
```

**Permission Issues**
```bash
# Make executable after build
chmod +x dist/gsai
```

### Build Failures

1. **Check uv installation**: `uv --version`
2. **Verify Python version**: `python --version` (should be 3.12+)
3. **Check API key format**: Ensure keys start with appropriate prefixes
4. **Review build logs**: Look for specific error messages

### Runtime Issues

If the built executable doesn't work:

1. **Test locally first**: `uv run python -m gsai --help`
2. **Check dependencies**: Ensure all required system libraries are available
3. **Verify API keys**: Use `./dist/gsai status` to check configuration

## Distribution

### Single File Distribution

The built executable is self-contained and can be distributed as a single file:

```bash
# Copy to target system
scp dist/gsai user@target-host:/usr/local/bin/

# Or create a distributable archive
tar -czf gsai-executable.tar.gz -C dist gsai
```

### Cross-Platform Builds

The executable is built for the current platform. For other platforms:

1. **Linux**: Build on Linux system or use Docker
2. **macOS**: Build on macOS system
3. **Windows**: Build on Windows system with appropriate tools

## Advanced Configuration

### Custom Build Configuration

Create a custom build configuration by modifying `build_executable.py`:

```python
# Custom PyInstaller options
spec_content = f'''
# Add custom options here
a = Analysis(
    ['gsai/main.py'],
    # Add custom paths, hidden imports, etc.
)
'''
```

### Build Optimization

For smaller executables:

```bash
# Build with UPX compression (if available)
python build_executable.py --optimize
```

## Support

For build issues:

1. Check this documentation
2. Review the build script logs
3. Ensure all prerequisites are met
4. Test with a minimal build first (`make build-test`)

The build system is designed to be robust and handle most common scenarios automatically.