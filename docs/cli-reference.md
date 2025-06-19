# CLI Reference

Complete command-line reference for GitStart CoPilot CLI.

## 📋 Overview

```bash
gsai [OPTIONS] COMMAND [ARGS]...
```

GitStart CoPilot CLI provides an interactive AI coding assistant with specialized capabilities for code writing, codebase exploration, and development workflow automation.

## 🚀 Global Options

### `--help, -h`
Show help message and exit.

```bash
gsai --help
gsai chat --help
```

### `--version`
Show version information.

```bash
gsai --version
# Output: GitStart CoPilot CLI v1.0.0
```

### `--verbose, -v`
Enable verbose output for debugging.

```bash
gsai --verbose chat
gsai -v status
```

### `--config`
Specify custom configuration file path.

```bash
gsai --config /path/to/custom/.env chat
```

## 🎯 Commands

### `chat`

Start an interactive AI coding session.

**Syntax:**
```bash
gsai chat [OPTIONS]
```

**Options:**

#### `--directory, -d`
Specify working directory (defaults to current directory).

```bash
gsai chat --directory /path/to/project
gsai chat -d ~/my-project
```

#### `--approval-mode`
Set approval mode for this session.

```bash
gsai chat --approval-mode suggest    # Safest (default)
gsai chat --approval-mode auto-edit  # Balanced
gsai chat --approval-mode full-auto  # Fastest (use with caution)
```

#### `--model`
Override default model for this session.

```bash
gsai chat --model openai:gpt-4
gsai chat --model anthropic:claude-3-sonnet-20240229
```

#### `--web-search / --no-web-search`
Enable or disable web search for this session.

```bash
gsai chat --web-search     # Enable web search
gsai chat --no-web-search  # Disable web search
```

#### `--verbose`
Enable verbose logging for debugging.

```bash
gsai chat --verbose
```

**Examples:**
```bash
# Basic chat session
gsai chat

# Chat in specific directory with auto-edit mode
gsai chat -d /path/to/project --approval-mode auto-edit

# Chat with web search enabled and specific model
gsai chat --web-search --model openai:gpt-4

# Full-auto mode for quick prototyping (use carefully)
gsai chat --approval-mode full-auto --verbose
```

### `configure`

Configure GitStart CoPilot CLI settings.

**Syntax:**
```bash
gsai configure [OPTIONS]
```

**Options:**

#### `--reset`
Reset configuration to defaults.

```bash
gsai configure --reset
```

#### `--import`
Import configuration from file.

```bash
gsai configure --import config.env
```

#### `--export`
Export current configuration to file.

```bash
gsai configure --export backup.env
```

#### `--migrate`
Migrate local configuration to global.

```bash
gsai configure --migrate
```

#### `--clear-cache`
Clear all cached data.

```bash
gsai configure --clear-cache
```

**Examples:**
```bash
# Interactive configuration
gsai configure

# Reset to defaults and reconfigure
gsai configure --reset

# Export current settings
gsai configure --export my-config.env

# Clear cache and reset
gsai configure --clear-cache --reset
```

### `status`

Show current configuration and system status.

**Syntax:**
```bash
gsai status [OPTIONS]
```

**Options:**

#### `--check`
Perform comprehensive system checks.

```bash
gsai status --check
```

#### `--verbose`
Show detailed configuration information.

```bash
gsai status --verbose
```

#### `--usage`
Show usage statistics.

```bash
gsai status --usage
```

#### `--test-apis`
Test API key connectivity.

```bash
gsai status --test-apis
```

**Example Output:**
```
GitStart CoPilot CLI Status
===========================

✓ Version: 1.0.0
✓ Configuration: ~/.ai/gsai/.env
✓ Working Directory: /current/path

API Keys:
✓ OpenAI API Key: Configured and valid
✓ Anthropic API Key: Configured and valid

Settings:
• Approval Mode: auto-edit
• Web Search: Enabled
• Cache: Enabled (156 MB, 1,234 entries)

Models:
• Coding Agent: anthropic:claude-3-sonnet-20240229
• QA Agent: openai:gpt-4
• Git Agent: openai:gpt-3.5-turbo

Usage (Today):
• Tokens Used: 45,231 / 100,000
• Requests Made: 23 / 50
```

### `version`

Show version information.

**Syntax:**
```bash
gsai version [OPTIONS]
```

**Options:**

#### `--short`
Show only version number.

```bash
gsai version --short
# Output: 1.0.0
```

#### `--full`
Show detailed version information.

```bash
gsai version --full
```

**Example Output:**
```
GitStart CoPilot CLI v1.0.0

Build Information:
• Built: 2024-01-15 10:30:00 UTC
• Commit: abc123def456
• Python: 3.12.0
• Platform: linux-x86_64

Dependencies:
• pydantic-ai: 0.2.6
• typer: 0.15.4
• rich: 13.0.0
```

## 🎨 Interactive Chat Commands

When in a chat session (`gsai chat`), you can use these special commands:

### `/help`
Show available chat commands.

```
You: /help
```

### `/exit` or `/quit`
Exit the chat session.

```
You: /exit
You: /quit
```

### `/clear`
Clear the conversation history.

```
You: /clear
```

### `/mode <mode>`
Change approval mode during session.

```
You: /mode suggest
You: /mode auto-edit
You: /mode full-auto
```

### `/status`
Show current session status.

```
You: /status
```

### `/save <filename>`
Save conversation to file.

```
You: /save my-conversation.md
```

### `/load <filename>`
Load conversation from file.

```
You: /load my-conversation.md
```

### `/model <model>`
Switch AI model during session.

```
You: /model openai:gpt-4
You: /model anthropic:claude-3-sonnet-20240229
```

### `/web-search <on|off>`
Toggle web search during session.

```
You: /web-search on
You: /web-search off
```

## 🔧 Environment Variables

You can override any configuration using environment variables:

### API Keys
```bash
export OPENAI_API_KEY="sk-your-openai-key"
export ANTHROPIC_API_KEY="sk-your-anthropic-key"
```

### Behavior Settings
```bash
export APPROVAL_MODE="auto-edit"        # suggest, auto-edit, full-auto
export WEB_SEARCH_ENABLED="true"        # true, false
export VERBOSE="false"                   # true, false
```

### Model Configuration
```bash
export MASTER_AGENT_MODEL_NAME="anthropic:claude-3-sonnet-20240229"
export CODING_AGENT_MODEL_NAME="anthropic:claude-3-sonnet-20240229"
export QA_AGENT_MODEL_NAME="openai:gpt-4"
export GIT_OPERATIONS_AGENT_MODEL_NAME="openai:gpt-3.5-turbo"
```

### Usage Limits
```bash
export MAX_TOKENS_PER_SESSION="100000"
export MAX_REQUESTS_PER_SESSION="50"
export MAX_DAILY_TOKENS="500000"
```

### Cache Settings
```bash
export CACHE_ENABLED="true"              # true, false
export CACHE_TTL_DAYS="30"               # number of days
export MAX_CACHE_SIZE_MB="1024"          # megabytes
export CACHE_STRATEGY="auto"             # auto, git, simple, full
```

### Logging
```bash
export LOG_LEVEL="INFO"                  # DEBUG, INFO, WARNING, ERROR
export LOG_FILE="/path/to/logfile.log"   # optional log file
```

## 📁 Configuration Files

### Global Configuration
**Location**: `~/.ai/gsai/.env`

This is the main configuration file that applies to all projects.

### Local Configuration
**Location**: `./.env` (in project directory)

Project-specific overrides. Values here override global settings.

### Configuration Priority
1. Command-line options (highest priority)
2. Environment variables
3. Local configuration file (`./.env`)
4. Global configuration file (`~/.ai/gsai/.env`)
5. Default values (lowest priority)

## 🔄 Exit Codes

GitStart CoPilot CLI uses these exit codes:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | API key error |
| 4 | Network error |
| 5 | Permission error |
| 130 | Interrupted by user (Ctrl+C) |

## 📝 Usage Examples

### Basic Workflow
```bash
# Check status
gsai status

# Configure if needed
gsai configure

# Start coding session
gsai chat

# Work in specific project
gsai chat -d ~/my-project --approval-mode auto-edit
```

### Advanced Usage
```bash
# Use specific model with web search
gsai chat --model openai:gpt-4 --web-search

# Debug session with verbose output
gsai chat --verbose --approval-mode suggest

# Quick prototype with full automation
gsai chat --approval-mode full-auto

# Export settings before experimenting
gsai configure --export backup.env
gsai configure --reset
# ... experiment ...
gsai configure --import backup.env
```

### Scripting
```bash
#!/bin/bash
# automated-review.sh

# Set up environment
export APPROVAL_MODE="suggest"
export LOG_LEVEL="INFO"

# Check status
if ! gsai status --check; then
    echo "Configuration issues detected"
    exit 1
fi

# Start review session
gsai chat --directory "$1" --model "anthropic:claude-3-sonnet-20240229"
```

## 🆘 Getting Help

### Command Help
```bash
# General help
gsai --help

# Command-specific help
gsai chat --help
gsai configure --help
gsai status --help
```

### Verbose Debugging
```bash
# Enable verbose output
gsai --verbose chat

# Check detailed status
gsai status --verbose --check
```

### Configuration Issues
```bash
# Reset everything
gsai configure --reset

# Test API connections
gsai status --test-apis

# Clear cache
gsai configure --clear-cache
```

---

**See also:** [Configuration Guide](configuration.md) | [Troubleshooting](troubleshooting.md) | [Quick Start](quick-start.md)