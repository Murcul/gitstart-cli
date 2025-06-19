# Configuration Guide

Complete guide to configuring GitStart CoPilot CLI for optimal performance and security.

## 🚀 Quick Configuration

### Interactive Setup
```bash
# Run interactive configuration
gsai configure
```

This wizard will guide you through:
- API key setup
- Approval mode selection
- Web search preferences
- Model preferences
- Usage limits

### Check Current Configuration
```bash
# View current settings
gsai status

# Show detailed configuration
gsai status --verbose
```

## 🔑 API Keys Configuration

GitStart CoPilot supports multiple AI providers. You need at least one API key to function.

### Supported Providers

#### OpenAI
- **Models**: GPT-4, GPT-3.5-turbo, GPT-4-turbo
- **Best for**: General coding, creative tasks
- **Get API Key**: [OpenAI Platform](https://platform.openai.com/api-keys)

#### Anthropic
- **Models**: Claude-3 Sonnet, Claude-3 Haiku, Claude-3 Opus
- **Best for**: Code analysis, complex reasoning
- **Get API Key**: [Anthropic Console](https://console.anthropic.com/)

### Setting API Keys

#### Method 1: Interactive Configuration
```bash
gsai configure
# Follow prompts to enter API keys
```

#### Method 2: Environment Variables
```bash
# Set environment variables
export OPENAI_API_KEY="sk-your-openai-key-here"
export ANTHROPIC_API_KEY="sk-your-anthropic-key-here"

# Make permanent (add to ~/.bashrc, ~/.zshrc, etc.)
echo 'export OPENAI_API_KEY="sk-your-openai-key-here"' >> ~/.bashrc
echo 'export ANTHROPIC_API_KEY="sk-your-anthropic-key-here"' >> ~/.bashrc
```

#### Method 3: Configuration File
```bash
# Edit configuration file directly
nano ~/.ai/gsai/.env
```

Add:
```env
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-your-anthropic-key-here
```

### API Key Security

#### File Permissions
```bash
# Configuration file is automatically secured
ls -la ~/.ai/gsai/.env
# Should show: -rw------- (600 permissions)

# If not secure, fix permissions
chmod 600 ~/.ai/gsai/.env
```

#### Key Validation
```bash
# Test API key validity
gsai status

# You'll see:
# ✓ OpenAI API Key: Valid
# ✓ Anthropic API Key: Valid
```

## ⚙️ Approval Modes

Control how much autonomy the AI has in making changes.

### Available Modes

#### `suggest` (Default - Safest)
- **Behavior**: AI suggests changes but doesn't make them
- **Use Case**: Learning, critical projects, first-time use
- **Security**: Highest - you approve everything

```bash
# Set suggest mode
gsai configure  # Then select "suggest"
# Or set temporarily
gsai chat --approval-mode suggest
```

#### `auto-edit` (Balanced)
- **Behavior**: AI can edit files, asks before running commands
- **Use Case**: Regular development, trusted projects
- **Security**: Medium - file changes automatic, commands require approval

```bash
# Set auto-edit mode
gsai configure  # Then select "auto-edit"
# Or set temporarily
gsai chat --approval-mode auto-edit
```

#### `full-auto` (Fastest)
- **Behavior**: AI can edit files and run commands without asking
- **Use Case**: Prototyping, experimental projects
- **Security**: Lowest - full autonomy (use with caution)

```bash
# Set full-auto mode
gsai configure  # Then select "full-auto"
# Or set temporarily
gsai chat --approval-mode full-auto
```

### Mode Comparison

| Feature | suggest | auto-edit | full-auto |
|---------|---------|-----------|-----------|
| File Reading | ✓ | ✓ | ✓ |
| File Editing | Manual approval | Automatic | Automatic |
| Command Execution | Manual approval | Manual approval | Automatic |
| Git Operations | Manual approval | Manual approval | Automatic |
| Safety Level | Highest | Medium | Lowest |
| Speed | Slowest | Medium | Fastest |

## 🌐 Web Search Configuration

Enable the AI to search the web for up-to-date information.

### Enable Web Search
```bash
# Enable via configuration
gsai configure
# Select "yes" for web search

# Or set environment variable
export WEB_SEARCH_ENABLED=true
```

### Disable Web Search
```bash
# Disable via configuration
gsai configure
# Select "no" for web search

# Or set environment variable
export WEB_SEARCH_ENABLED=false
```

### Web Search Features
- **Documentation lookup**: Find API documentation
- **Error resolution**: Search for solutions to error messages
- **Technology updates**: Get information about latest versions
- **Best practices**: Find current coding standards

## 🧠 Model Configuration

Customize which AI models are used for different tasks.

### Available Models

#### OpenAI Models
```env
# GPT-4 (Recommended)
CODING_AGENT_MODEL_NAME=openai:gpt-4-turbo
QUESTION_ANSWERING_AGENT_MODEL_NAME=openai:gpt-4

# GPT-3.5 (Faster, cheaper)
CODING_AGENT_MODEL_NAME=openai:gpt-3.5-turbo
```

#### Anthropic Models
```env
# Claude-3 Sonnet (Recommended)
CODING_AGENT_MODEL_NAME=anthropic:claude-3-sonnet-20240229
QUESTION_ANSWERING_AGENT_MODEL_NAME=anthropic:claude-3-sonnet-20240229

# Claude-3 Haiku (Faster)
CODING_AGENT_MODEL_NAME=anthropic:claude-3-haiku-20240307
```

### Model Specialization

Different agents can use different models:

```env
# Specialized configuration
CODING_AGENT_MODEL_NAME=anthropic:claude-3-sonnet-20240229
QUESTION_ANSWERING_AGENT_MODEL_NAME=openai:gpt-4
GIT_OPERATIONS_AGENT_MODEL_NAME=openai:gpt-3.5-turbo
IMPLEMENTATION_PLAN_AGENT_MODEL_NAME=anthropic:claude-3-sonnet-20240229
```

### Configure Models

#### Via Configuration File
```bash
# Edit configuration
nano ~/.ai/gsai/.env

# Add model preferences
MASTER_AGENT_MODEL_NAME=anthropic:claude-3-sonnet-20240229
CODING_AGENT_MODEL_NAME=anthropic:claude-3-sonnet-20240229
QA_AGENT_MODEL_NAME=openai:gpt-4
```

#### Via Environment Variables
```bash
export CODING_AGENT_MODEL_NAME="anthropic:claude-3-sonnet-20240229"
export QA_AGENT_MODEL_NAME="openai:gpt-4"
```

## 📊 Usage Limits

Control resource usage and costs.

### Set Limits

```env
# Token limits per session
MAX_TOKENS_PER_SESSION=100000

# Request limits per session
MAX_REQUESTS_PER_SESSION=50

# Daily usage limits
MAX_DAILY_TOKENS=500000
MAX_DAILY_REQUESTS=200
```

### Monitor Usage
```bash
# Check current usage
gsai status --usage

# Reset usage counters
gsai configure --reset-usage
```

## 📁 Configuration File Reference

### Location
- **Global Config**: `~/.ai/gsai/.env`
- **Local Config**: `./.env` (project-specific, optional)

### Complete Configuration Example

```env
# ~/.ai/gsai/.env

# API Keys
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-your-anthropic-key-here

# Security Settings
APPROVAL_MODE=auto-edit
WEB_SEARCH_ENABLED=true

# Model Configuration
MASTER_AGENT_MODEL_NAME=anthropic:claude-3-sonnet-20240229
CODING_AGENT_MODEL_NAME=anthropic:claude-3-sonnet-20240229
QA_AGENT_MODEL_NAME=openai:gpt-4
GIT_OPERATIONS_AGENT_MODEL_NAME=openai:gpt-3.5-turbo
IMPLEMENTATION_PLAN_AGENT_MODEL_NAME=anthropic:claude-3-sonnet-20240229

# Usage Limits
MAX_TOKENS_PER_SESSION=100000
MAX_REQUESTS_PER_SESSION=50

# Logging
LOG_LEVEL=INFO
VERBOSE=false

# Cache Settings
CACHE_ENABLED=true
CACHE_TTL_DAYS=30
MAX_CACHE_SIZE_MB=1024
```

## 🔧 Advanced Configuration

### Cache Settings

```env
# Enable/disable caching
CACHE_ENABLED=true

# Cache time-to-live
CACHE_TTL_DAYS=30

# Maximum cache size
MAX_CACHE_SIZE_MB=1024

# Cache strategy
CACHE_STRATEGY=auto  # auto, git, simple, full
```

### Logging Configuration

```env
# Log level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Verbose output
VERBOSE=false

# Log file location (optional)
LOG_FILE=~/.ai/gsai/logs/gsai.log
```

### Working Directory Settings

```env
# Default working directory
WORKING_DIRECTORY=.

# Restrict operations to working directory
RESTRICT_TO_WORKDIR=true
```

## 🔄 Migration and Backup

### Migrate Configuration

```bash
# Migrate from local to global config
gsai configure --migrate

# Import configuration from file
gsai configure --import config.env

# Export current configuration
gsai configure --export backup.env
```

### Backup Configuration

```bash
# Backup current configuration
cp ~/.ai/gsai/.env ~/.ai/gsai/.env.backup

# Restore from backup
cp ~/.ai/gsai/.env.backup ~/.ai/gsai/.env
```

## 🏢 Team Configuration

### Shared Configuration

For teams, create a shared configuration template:

```bash
# Create team template
cat > team-config-template.env << 'EOF'
# Team Configuration Template
APPROVAL_MODE=auto-edit
WEB_SEARCH_ENABLED=true
LOG_LEVEL=INFO

# Model preferences
CODING_AGENT_MODEL_NAME=anthropic:claude-3-sonnet-20240229
QA_AGENT_MODEL_NAME=openai:gpt-4

# Usage limits
MAX_TOKENS_PER_SESSION=50000
MAX_REQUESTS_PER_SESSION=25
EOF

# Team members copy and customize
cp team-config-template.env ~/.ai/gsai/.env
# Then add personal API keys
```

### Project-Specific Configuration

```bash
# Create project-specific config
cd your-project
cat > .env << 'EOF'
# Project-specific overrides
APPROVAL_MODE=suggest
WEB_SEARCH_ENABLED=false
LOG_LEVEL=DEBUG
EOF
```

## 🛠️ Configuration Troubleshooting

### Common Issues

#### Configuration Not Found
```bash
# Create configuration directory
mkdir -p ~/.ai/gsai

# Run configuration wizard
gsai configure
```

#### Permission Denied
```bash
# Fix permissions
chmod 700 ~/.ai/gsai
chmod 600 ~/.ai/gsai/.env
```

#### Invalid API Keys
```bash
# Validate keys
gsai status

# Reconfigure if invalid
gsai configure
```

#### Configuration Not Loading
```bash
# Check file exists
ls -la ~/.ai/gsai/.env

# Check file format
cat ~/.ai/gsai/.env

# Recreate if corrupted
rm ~/.ai/gsai/.env
gsai configure
```

### Reset Configuration

```bash
# Reset to defaults
gsai configure --reset

# Clear all configuration
rm -rf ~/.ai/gsai
gsai configure
```

## 📞 Getting Help

### Configuration Commands
```bash
# View all configuration options
gsai configure --help

# Show current configuration
gsai status --verbose

# Validate configuration
gsai status --check
```

### Debug Configuration Issues
```bash
# Enable verbose logging
gsai chat --verbose

# Check environment variables
env | grep -E "(OPENAI|ANTHROPIC|GSAI)"

# Test API connections
gsai status --test-apis
```

---

**Next:** [Basic Usage](usage.md) | **See also:** [CLI Reference](cli-reference.md)