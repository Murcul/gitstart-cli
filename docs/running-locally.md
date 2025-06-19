# Running GitStart CoPilot CLI Locally

This guide explains all the ways to run GitStart CoPilot CLI locally, especially for development and when the pre-built executables have issues.

## 🚀 Quick Local Run (Development)

### Method 1: Direct Execution with uv (Recommended)

```bash
# Clone and enter the project
git clone https://github.com/your-org/gitstart-cli.git
cd gitstart-cli

# Install dependencies
uv sync

# Run directly without installation
uv run gsai --help
uv run gsai chat

# Or run as module
uv run python -m gsai chat
```

### Method 2: Global Installation with uv

```bash
# Install dependencies
uv sync

# Install globally
uv tool install .

# Run from anywhere
gsai --help
gsai chat
```

### Method 3: Development Mode with pip

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Run normally
gsai chat
```

## 🔧 Fixing the PyInstaller Issue

### The Problem

You might see this error with pre-built executables:

```
PackageNotFoundError: No package metadata was found for pydantic_ai_slim
```

This is a known PyInstaller packaging issue where package metadata isn't properly included in the bundled executable.

### Solutions

#### Solution 1: Run from Source (Recommended)

```bash
# Clone repository
git clone https://github.com/your-org/gitstart-cli.git
cd gitstart-cli

# Install uv if not available
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run directly
uv sync
uv run gsai chat
```

#### Solution 2: Create a Fixed Executable

The PyInstaller configuration needs to be updated to properly include package metadata. For now, running from source is the most reliable option.

#### Solution 3: Use Docker (If Available)

```bash
# Pull and run via Docker
docker run -it --rm \
  -v "$(pwd):/workspace" \
  -w /workspace \
  gitstart/copilot-cli:latest gsai chat
```

## 📋 Development Workflow

### For Regular Development

```bash
# Set up development environment
cd gitstart-cli
uv sync --dev

# Run with hot reload during development
uv run gsai chat

# Run tests
uv run pytest

# Check code quality
uv run ruff format
uv run mypy .
```

### For Testing Builds

```bash
# Test local build
./build-local.sh

# If successful, test the executable
./dist/gsai --help
./dist/gsai chat
```

## ⚙️ Configuration for Local Development

### Set Up API Keys

```bash
# Method 1: Use gsai configure
uv run gsai configure

# Method 2: Environment variables
export OPENAI_API_KEY="sk-your-openai-key"
export ANTHROPIC_API_KEY="sk-your-anthropic-key"

# Method 3: Create local .env file
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-your-anthropic-key
APPROVAL_MODE=auto-edit
WEB_SEARCH_ENABLED=true
EOF
```

### Check Configuration

```bash
# Verify setup
uv run gsai status

# Test API connections
uv run gsai status --test-apis
```

## 🛠️ Platform-Specific Local Setup

### Linux/macOS

```bash
# Install prerequisites
# Ubuntu/Debian:
sudo apt update && sudo apt install python3.12 python3.12-venv git curl

# macOS:
brew install python@3.12 git

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and run
git clone https://github.com/your-org/gitstart-cli.git
cd gitstart-cli
uv sync
uv run gsai chat
```

### Windows

```powershell
# Install Python 3.12+ from python.org
# Install Git for Windows

# Install uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Clone and run
git clone https://github.com/your-org/gitstart-cli.git
cd gitstart-cli
uv sync
uv run gsai chat
```

## 🔍 Debugging Local Issues

### Common Issues and Solutions

#### uv not found
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc
```

#### Python version issues
```bash
# Check Python version
python3 --version

# Install Python 3.12+ if needed
# Ubuntu: sudo apt install python3.12
# macOS: brew install python@3.12
# Windows: Download from python.org
```

#### Import errors
```bash
# Reinstall dependencies
uv sync --dev

# Clear Python cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

#### API key issues
```bash
# Check configuration
uv run gsai status

# Reconfigure
uv run gsai configure

# Test keys manually
uv run gsai status --test-apis
```

### Debug Mode

```bash
# Run with verbose output
uv run gsai chat --verbose

# Enable debug logging
export LOG_LEVEL=DEBUG
uv run gsai chat

# Save logs
uv run gsai chat --verbose 2>&1 | tee debug.log
```

## 🚀 Performance Tips for Local Development

### Faster Startup

```bash
# Use environment variables instead of config file
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-..."
export APPROVAL_MODE="auto-edit"

# Skip unnecessary checks
export CACHE_ENABLED=false
```

### Development Shortcuts

```bash
# Create aliases for convenience
echo 'alias gsai-dev="cd /path/to/gitstart-cli && uv run gsai"' >> ~/.bashrc
echo 'alias gsai-chat="cd /path/to/gitstart-cli && uv run gsai chat"' >> ~/.bashrc

# Source the aliases
source ~/.bashrc

# Now use shortcuts
gsai-chat
```

## 📦 Creating Your Own Distribution

### Build Local Executable

```bash
# Build with embedded API keys
./build-local.sh

# Or with custom API keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-..."
python3 build_executable.py \
  --openai-key "$OPENAI_API_KEY" \
  --anthropic-key "$ANTHROPIC_API_KEY"
```

### Test Your Build

```bash
# Test the executable
./dist/gsai --help
./dist/gsai version
./dist/gsai status
./dist/gsai chat
```

## 🆘 Getting Help

### If Local Setup Fails

1. **Check prerequisites:**
   ```bash
   python3 --version  # Should be 3.12+
   uv --version       # Should work
   git --version      # Should work
   ```

2. **Verify project structure:**
   ```bash
   ls pyproject.toml  # Should exist
   ls gsai/main.py    # Should exist
   ```

3. **Clean and retry:**
   ```bash
   # Clean everything
   rm -rf .venv
   rm -rf __pycache__
   find . -name "*.pyc" -delete
   
   # Start fresh
   uv sync
   uv run gsai --help
   ```

4. **Check for known issues:**
   - [Troubleshooting Guide](troubleshooting.md)
   - [FAQ](faq.md)
   - GitHub Issues

### Report Issues

If you can't get it running locally:

1. **Collect debug information:**
   ```bash
   # System info
   uname -a
   python3 --version
   uv --version
   
   # Try running with debug
   uv run gsai --verbose chat 2>&1 | tee debug.log
   ```

2. **Open an issue** with:
   - Your operating system
   - Python version
   - Error messages
   - Steps you tried

---

**Running locally is often more reliable than pre-built executables during development.** The source-based approach gives you full control and easier debugging.

**See also:** [Quick Start Guide](quick-start.md) | [Configuration Guide](configuration.md) | [Troubleshooting](troubleshooting.md)