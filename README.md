# GitStart AI CLI

Interactive AI coding assistant with encrypted embedded API keys for immediate use.

## Quick Install

### Windows
```powershell
iwr -useb https://github.com/YOUR-REPO/gitstart-cli/releases/latest/download/install.ps1 | iex
```

### Linux/macOS
```bash
curl -sSL https://github.com/YOUR-REPO/gitstart-cli/releases/latest/download/install.sh | bash
```

### Manual Download
Download the appropriate executable from [Releases](https://github.com/YOUR-REPO/gitstart-cli/releases):
- Windows: `gsai-VERSION-windows-x86_64.zip`
- macOS: `gsai-VERSION-macos-x86_64.zip`  
- Linux: `gsai-VERSION-linux-x86_64.zip`

## Usage

```bash
# Start AI coding session
gsai chat

# Check configuration
gsai status

# Configure API keys (if needed)
gsai configure

# Show help
gsai --help
```

## Features

- **Zero Setup**: Production builds include embedded encrypted API keys
- **Cross-Platform**: Windows, macOS, Linux support
- **Secure**: AES-256 encrypted API key embedding
- **Interactive**: Rich terminal interface with syntax highlighting
- **Flexible**: Multiple approval modes for different workflows

## Approval Modes

- **suggest**: Read-only mode, requires approval for all changes
- **auto-edit**: Can edit files, requires approval for commands  
- **full-auto**: Can edit files and run commands without approval

## Development

### Requirements
- Python 3.12+
- uv package manager

### Setup
```bash
git clone <repository-url>
cd gitstart-cli
uv sync --dev
```

### Run from Source
```bash
uv run gsai chat
```

### Build
```bash
uv run python scripts/build_with_keys.py  # Embed API keys
uv run pyinstaller gsai.spec               # Build executable
```

## Configuration

### API Keys Priority
1. Environment variables (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`)
2. User configuration (`~/.ai/gsai/.env`)
3. Embedded keys (production builds)

### Global Configuration
Location: `~/.ai/gsai/.env`

```bash
# Configure interactively
gsai configure

# Or set environment variables
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
```

## Architecture

The CLI uses a multi-agent system:
- **Master Agent**: Orchestrates tasks and provides unified interface
- **Specialized Agents**: Handle specific domains (coding, Q&A, git, planning)
- **Security Layer**: Enforces approval workflows and path validation
- **Tool Ecosystem**: File operations, code analysis, development tools

## License

MIT License - see LICENSE file for details.