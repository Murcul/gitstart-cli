# Troubleshooting Guide

Common issues and solutions for GitStart CoPilot CLI.

## 🚨 Quick Diagnostics

### Run Health Check
```bash
# Comprehensive system check
gsai status --check

# Verbose diagnostic information
gsai status --verbose

# Test API connections
gsai status --test-apis
```

### Common Quick Fixes
```bash
# Reset configuration
gsai configure --reset

# Clear cache
gsai configure --clear-cache

# Reinstall (if using uv)
uv tool uninstall gsai && uv tool install .
```

## 🔧 Installation Issues

### Command Not Found: `gsai`

**Symptoms:**
```bash
$ gsai
bash: gsai: command not found
```

**Solutions:**

#### Check Installation Location
```bash
# Find gsai binary
which gsai
whereis gsai

# Common locations to check
ls -la /usr/local/bin/gsai
ls -la ~/.local/bin/gsai
ls -la /opt/homebrew/bin/gsai  # macOS Homebrew
```

#### Fix PATH Issues
```bash
# Add to PATH temporarily
export PATH="/usr/local/bin:$PATH"

# Make permanent (choose your shell)
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc    # Bash
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc     # Zsh
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.profile   # Generic

# Reload shell
source ~/.bashrc  # or ~/.zshrc
```

#### Reinstall Binary
```bash
# Download and install again
curl -L -o gsai https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-$(uname -s | tr '[:upper:]' '[:lower:]')-x86_64
chmod +x gsai
sudo mv gsai /usr/local/bin/
```

### Permission Denied

**Symptoms:**
```bash
$ gsai
bash: /usr/local/bin/gsai: Permission denied
```

**Solutions:**
```bash
# Fix permissions
sudo chmod +x /usr/local/bin/gsai

# Or install to user directory
mkdir -p ~/.local/bin
mv gsai ~/.local/bin/
export PATH="$HOME/.local/bin:$PATH"
```

### Python Version Issues

**Symptoms:**
```bash
ImportError: Python 3.12 or higher is required
```

**Solutions:**

#### Check Python Version
```bash
python3 --version
python3.12 --version  # If available
```

#### Install Python 3.12+

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev
```

**macOS:**
```bash
# Using Homebrew
brew install python@3.12

# Using pyenv
pyenv install 3.12.0
pyenv global 3.12.0
```

**CentOS/RHEL:**
```bash
# Enable EPEL repository first
sudo dnf install epel-release
sudo dnf install python3.12
```

## 🔑 API Key Issues

### No API Keys Configured

**Symptoms:**
```bash
Error: No API keys configured. Please run 'gsai configure'
```

**Solutions:**
```bash
# Configure interactively
gsai configure

# Or set environment variables
export OPENAI_API_KEY="sk-your-key"
export ANTHROPIC_API_KEY="sk-your-key"

# Make permanent
echo 'export OPENAI_API_KEY="sk-your-key"' >> ~/.bashrc
```

### Invalid API Keys

**Symptoms:**
```bash
Error: Invalid OpenAI API key
Error: Anthropic API key authentication failed
```

**Solutions:**

#### Verify API Keys
```bash
# Check key format
echo $OPENAI_API_KEY | grep -E '^sk-[a-zA-Z0-9]{48}$'     # OpenAI format
echo $ANTHROPIC_API_KEY | grep -E '^sk-ant-[a-zA-Z0-9-]+$' # Anthropic format

# Test manually
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

#### Get New API Keys
- **OpenAI**: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Anthropic**: [https://console.anthropic.com/](https://console.anthropic.com/)

#### Check API Key Permissions
```bash
# Verify account has credits/usage available
gsai status --test-apis
```

### Configuration File Issues

**Symptoms:**
```bash
Error: Could not read configuration file
```

**Solutions:**
```bash
# Check if config exists
ls -la ~/.ai/gsai/.env

# Check permissions
chmod 600 ~/.ai/gsai/.env

# Recreate if corrupted
rm ~/.ai/gsai/.env
gsai configure
```

## 🌐 Network and Connection Issues

### SSL Certificate Errors

**Symptoms:**
```bash
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solutions:**

#### Update Certificates
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ca-certificates

# macOS
brew install ca-certificates
# Or update Python certificates
/Applications/Python\ 3.12/Install\ Certificates.command

# CentOS/RHEL
sudo dnf update ca-certificates
```

#### Python Certificate Issues
```bash
# Install certificates for Python
pip install --upgrade certifi

# Update Python SSL module
python3 -m pip install --upgrade pip setuptools
```

### Proxy Issues

**Symptoms:**
```bash
ProxyError: HTTPSConnectionPool
```

**Solutions:**
```bash
# Set proxy environment variables
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
export NO_PROXY=localhost,127.0.0.1

# For authentication
export HTTP_PROXY=http://username:password@proxy.company.com:8080
```

### API Rate Limiting

**Symptoms:**
```bash
Error: Rate limit exceeded
Error: Too many requests
```

**Solutions:**
```bash
# Check current usage
gsai status --usage

# Set usage limits
gsai configure
# Then set lower limits

# Wait and retry
sleep 60
gsai chat
```

## 💻 Runtime Issues

### Memory Issues

**Symptoms:**
```bash
MemoryError: Unable to allocate memory
Process killed (OOM)
```

**Solutions:**
```bash
# Check system memory
free -h

# Clear cache
gsai configure --clear-cache

# Reduce model complexity (use smaller models)
export CODING_AGENT_MODEL_NAME="openai:gpt-3.5-turbo"
```

### Performance Issues

**Symptoms:**
- Slow responses
- High CPU usage
- Long processing times

**Solutions:**
```bash
# Clear cache
gsai configure --clear-cache

# Use faster models
export CODING_AGENT_MODEL_NAME="openai:gpt-3.5-turbo"
export QA_AGENT_MODEL_NAME="anthropic:claude-3-haiku-20240307"

# Reduce context size
export MAX_TOKENS_PER_SESSION=50000

# Disable web search if not needed
export WEB_SEARCH_ENABLED=false
```

### File Permission Issues

**Symptoms:**
```bash
PermissionError: [Errno 13] Permission denied
```

**Solutions:**
```bash
# Check file permissions
ls -la .

# Fix ownership
sudo chown -R $(whoami) .

# Run in safe directory
cd ~/tmp
gsai chat
```

## 🐛 Application Errors

### Import Errors

**Symptoms:**
```bash
ModuleNotFoundError: No module named 'pydantic_ai'
ImportError: cannot import name 'something'
```

**Solutions:**
```bash
# Reinstall dependencies
uv sync --dev

# Clear Python cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# Reinstall completely
uv tool uninstall gsai
uv tool install .
```

### Configuration Errors

**Symptoms:**
```bash
ValidationError: Invalid configuration
KeyError: 'OPENAI_API_KEY'
```

**Solutions:**
```bash
# Reset configuration
gsai configure --reset

# Validate configuration
gsai status --check

# Fix specific issues
gsai configure
```

### Agent Communication Errors

**Symptoms:**
```bash
Error: Agent failed to respond
Timeout: Request timed out
```

**Solutions:**
```bash
# Check network connectivity
curl -I https://api.openai.com
curl -I https://api.anthropic.com

# Increase timeout
export REQUEST_TIMEOUT=120

# Restart session
exit
gsai chat
```

## 📱 Platform-Specific Issues

### macOS Issues

#### Gatekeeper Blocking Execution
```bash
# Remove quarantine
sudo xattr -rd com.apple.quarantine /usr/local/bin/gsai

# Or allow in System Preferences
# Security & Privacy → General → Allow apps downloaded from
```

#### Homebrew Issues
```bash
# Update Homebrew
brew update

# Fix permissions
sudo chown -R $(whoami) /usr/local/bin

# Reinstall
brew uninstall gsai
brew install gitstart/cli/gsai
```

### Linux Issues

#### Missing Libraries
```bash
# Install required system libraries
sudo apt install libssl-dev libffi-dev python3-dev build-essential  # Ubuntu/Debian
sudo dnf install openssl-devel libffi-devel python3-devel gcc       # CentOS/RHEL
sudo pacman -S openssl libffi python base-devel                     # Arch Linux
```

#### AppArmor/SELinux Issues
```bash
# Check if AppArmor is blocking
sudo aa-status | grep gsai

# Temporarily disable (not recommended for production)
sudo aa-complain /usr/local/bin/gsai

# Check SELinux
sestatus
sudo setsebool -P allow_execstack 1
```

### Windows Issues (If supported)

#### PowerShell Execution Policy
```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or bypass for single command
powershell -ExecutionPolicy Bypass -File script.ps1
```

## 🔍 Debug Mode

### Enable Verbose Logging
```bash
# Verbose mode
gsai chat --verbose

# Set log level
export LOG_LEVEL=DEBUG
gsai chat

# Save logs to file
gsai chat --verbose 2>&1 | tee debug.log
```

### Collect Debug Information
```bash
# System information
uname -a
python3 --version
gsai --version

# Configuration status
gsai status --verbose

# Environment variables
env | grep -E "(OPENAI|ANTHROPIC|GSAI|PATH)"

# Disk space
df -h

# Memory usage
free -h
```

## 📞 Getting Additional Help

### Before Asking for Help

Collect this information:

```bash
# Create debug report
cat > debug-report.txt << EOF
System: $(uname -a)
Python: $(python3 --version)
GSAI Version: $(gsai --version)
Configuration Status:
$(gsai status --verbose)

Environment Variables:
$(env | grep -E "(OPENAI|ANTHROPIC|GSAI|PATH)")

Error Message:
[Paste your error message here]

Steps to Reproduce:
1. [What you did]
2. [What happened]
3. [What you expected]
EOF
```

### Where to Get Help

1. **Documentation**: Check other guides in `/docs`
2. **GitHub Issues**: [Report bugs](https://github.com/your-org/gitstart-cli/issues)
3. **Discussions**: [Community help](https://github.com/your-org/gitstart-cli/discussions)
4. **Stack Overflow**: Tag with `gitstart-cli`

### Emergency Recovery

If completely broken:

```bash
# Nuclear option - complete reset
rm -rf ~/.ai/gsai
uv tool uninstall gsai
curl -L -o gsai https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-$(uname -s | tr '[:upper:]' '[:lower:]')-x86_64
chmod +x gsai
sudo mv gsai /usr/local/bin/
gsai configure
```

---

**Still having issues?** Check the [FAQ](faq.md) or open an issue on [GitHub](https://github.com/your-org/gitstart-cli/issues).