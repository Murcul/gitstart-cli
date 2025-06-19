# Frequently Asked Questions (FAQ)

Common questions and answers about GitStart CoPilot CLI.

## 🚀 Getting Started

### Q: What is GitStart CoPilot CLI?
**A:** GitStart CoPilot CLI is an interactive command-line interface that provides an AI coding assistant. It helps you write code, explore codebases, debug issues, and automate development workflows using advanced AI models from OpenAI and Anthropic.

### Q: Do I need to install Python to use the pre-built executables?
**A:** No! The pre-built executables are self-contained and include everything you need. Just download, make executable, and run. No Python installation required.

### Q: Which AI providers are supported?
**A:** Currently supported:
- **OpenAI**: GPT-4, GPT-4-turbo, GPT-3.5-turbo
- **Anthropic**: Claude-3 Sonnet, Claude-3 Haiku, Claude-3 Opus

You need at least one API key to use the CLI.

### Q: Is GitStart CoPilot CLI free?
**A:** The CLI itself is free, but you'll need API keys from OpenAI or Anthropic, which have their own pricing. Both providers offer free tiers to get started.

## 🔑 API Keys and Configuration

### Q: Where do I get API keys?
**A:** 
- **OpenAI**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Anthropic**: [console.anthropic.com](https://console.anthropic.com/)

Both providers require account creation and may require payment information for higher usage tiers.

### Q: How are my API keys stored?
**A:** API keys are stored securely in `~/.ai/gsai/.env` with restricted permissions (600). The file is only readable by your user account.

### Q: Can I use both OpenAI and Anthropic keys simultaneously?
**A:** Yes! You can configure both and the CLI will use the appropriate provider for different tasks. Some features work better with specific models.

### Q: What happens if my API key is invalid?
**A:** The CLI will detect invalid keys during startup and provide clear error messages. Run `gsai status --test-apis` to verify your keys.

### Q: How much will API usage cost?
**A:** Costs depend on usage patterns:
- **Light usage** (occasional help): $1-5/month
- **Regular usage** (daily coding): $10-30/month  
- **Heavy usage** (all-day assistant): $50+/month

Both providers offer usage dashboards to monitor costs.

## 🛡️ Security and Safety

### Q: Is my code sent to AI providers?
**A:** Yes, the code context necessary for AI assistance is sent to the AI providers. However:
- Only relevant code snippets are sent, not entire codebases
- You control what gets shared through approval modes
- Data is transmitted over encrypted connections
- Review each provider's privacy policy for data retention

### Q: What are approval modes?
**A:** Approval modes control how much autonomy the AI has:
- **`suggest`**: AI suggests changes, you approve each one (safest)
- **`auto-edit`**: AI can edit files, asks before running commands
- **`full-auto`**: AI can edit files and run commands without asking (use carefully)

### Q: Can the AI delete my files?
**A:** Only if you:
1. Use `full-auto` mode AND
2. Explicitly ask the AI to delete files

In `suggest` and `auto-edit` modes, all destructive operations require your approval.

### Q: Should I use this on production code?
**A:** Recommendations by approval mode:
- **`suggest`**: Generally safe for any environment
- **`auto-edit`**: Safe for development, review changes before production
- **`full-auto`**: Only in development/test environments

Always commit your work before starting AI sessions.

## 💻 Installation and Technical Issues

### Q: I'm getting "command not found: gsai"
**A:** This means `gsai` isn't in your PATH. Solutions:
```bash
# Check if gsai exists
which gsai

# Add to PATH (choose your shell)
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc

# Reload shell
source ~/.bashrc
```

### Q: I get "Permission denied" when running gsai
**A:** Fix with:
```bash
# Make executable
chmod +x /usr/local/bin/gsai

# Or install to user directory
mkdir -p ~/.local/bin
mv gsai ~/.local/bin/
export PATH="$HOME/.local/bin:$PATH"
```

### Q: The executable shows "PackageNotFoundError: pydantic_ai_slim"
**A:** This is a known PyInstaller packaging issue. Solutions:
1. **Download a newer release** (we're working on fixing this)
2. **Install from source** instead:
   ```bash
   git clone https://github.com/your-org/gitstart-cli.git
   cd gitstart-cli
   uv sync && uv tool install .
   ```
3. **Use the development version**:
   ```bash
   uv run gsai chat
   ```

### Q: I need Python 3.12 but my system has an older version
**A:** Install Python 3.12:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.12
```

**macOS:**
```bash
brew install python@3.12
```

**Or use pyenv for version management:**
```bash
curl https://pyenv.run | bash
pyenv install 3.12.0
pyenv global 3.12.0
```

## 🎯 Usage and Features

### Q: How do I start using the AI assistant?
**A:** 
```bash
# Navigate to your project
cd your-project

# Start AI session
gsai chat

# Or specify directory
gsai chat --directory /path/to/project
```

### Q: What can I ask the AI to do?
**A:** The AI can help with:
- **Code writing**: "Create a function to validate email addresses"
- **Debugging**: "Fix this error in line 42 of main.py"
- **Code review**: "Review my recent changes and suggest improvements"
- **Explanation**: "What does this function do?"
- **Refactoring**: "Improve the performance of this code"
- **Documentation**: "Add docstrings to this module"
- **Git operations**: "Create a commit for these changes"

### Q: How do I exit a chat session?
**A:** Type any of:
- `exit`
- `quit`
- Press `Ctrl+C`

### Q: Can I save conversation history?
**A:** Yes! Use in-chat commands:
```
You: /save my-conversation.md
You: /load previous-conversation.md
```

### Q: How do I change AI models during a session?
**A:** Use the `/model` command:
```
You: /model openai:gpt-4
You: /model anthropic:claude-3-sonnet-20240229
```

### Q: What's the difference between AI models?
**A:** 
- **GPT-4**: Excellent for creative coding, complex problem-solving
- **GPT-3.5-turbo**: Faster, cheaper, good for simple tasks
- **Claude-3 Sonnet**: Great for code analysis, detailed explanations
- **Claude-3 Haiku**: Fastest, good for quick questions

## 🔧 Advanced Configuration

### Q: Can I use different models for different tasks?
**A:** Yes! Configure in `~/.ai/gsai/.env`:
```env
CODING_AGENT_MODEL_NAME=anthropic:claude-3-sonnet-20240229
QA_AGENT_MODEL_NAME=openai:gpt-4
GIT_OPERATIONS_AGENT_MODEL_NAME=openai:gpt-3.5-turbo
```

### Q: How do I limit API usage to control costs?
**A:** Set usage limits:
```env
MAX_TOKENS_PER_SESSION=50000
MAX_REQUESTS_PER_SESSION=25
MAX_DAILY_TOKENS=200000
```

### Q: Can I use this in a team environment?
**A:** Yes! Create a team configuration template:
```bash
# Create shared template
cat > team-config.env << 'EOF'
APPROVAL_MODE=auto-edit
WEB_SEARCH_ENABLED=true
CODING_AGENT_MODEL_NAME=anthropic:claude-3-sonnet-20240229
MAX_TOKENS_PER_SESSION=50000
EOF

# Team members customize with their API keys
```

### Q: How do I enable web search?
**A:** 
```bash
# Via configuration
gsai configure
# Select "yes" for web search

# Or set environment variable
export WEB_SEARCH_ENABLED=true

# Or in chat session
You: /web-search on
```

### Q: What does the cache do and should I enable it?
**A:** The cache stores:
- Code analysis results
- File structure maps
- Common AI responses

Benefits: Faster responses, reduced API costs
Recommended: Keep enabled unless you have disk space constraints

## 🚨 Troubleshooting

### Q: The AI gives incorrect or outdated information
**A:** Try:
1. Enable web search for current information
2. Be more specific in your requests
3. Use newer models (GPT-4, Claude-3 Sonnet)
4. Clear cache: `gsai configure --clear-cache`

### Q: Responses are very slow
**A:** 
1. Use faster models: `gpt-3.5-turbo` or `claude-3-haiku`
2. Reduce context with smaller projects
3. Disable web search if not needed
4. Check your internet connection

### Q: I'm hitting API rate limits
**A:** 
1. Check current usage: `gsai status --usage`
2. Reduce usage limits in configuration
3. Upgrade your API plan with the provider
4. Wait for rate limits to reset (usually 1 hour)

### Q: The AI won't modify certain files
**A:** Check:
1. File permissions (make sure files are writable)
2. Approval mode (use `auto-edit` or `full-auto`)
3. Working directory restrictions
4. File is not in `.gitignore` or excluded patterns

## 🔄 Updates and Maintenance

### Q: How do I update GitStart CoPilot CLI?
**A:** Depends on installation method:

**Pre-built executable:**
```bash
# Download latest release
curl -L -o gsai-new https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-linux-x86_64
sudo mv gsai-new /usr/local/bin/gsai
sudo chmod +x /usr/local/bin/gsai
```

**Homebrew:**
```bash
brew update && brew upgrade gsai
```

**From source:**
```bash
cd gitstart-cli
git pull origin main
uv tool install . --force
```

### Q: How do I reset everything if something goes wrong?
**A:** Nuclear reset:
```bash
# Remove configuration
rm -rf ~/.ai/gsai

# Reinstall (if using uv)
uv tool uninstall gsai
uv tool install .

# Or download fresh executable
curl -L -o gsai https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-linux-x86_64
chmod +x gsai && sudo mv gsai /usr/local/bin/

# Reconfigure
gsai configure
```

### Q: Where are logs stored?
**A:** 
- Configuration: `~/.ai/gsai/.env`
- Cache: `~/.ai/gsai/cache/`
- Logs: Usually displayed in terminal, can be saved with `--verbose`

### Q: How do I completely uninstall?
**A:** 
```bash
# Remove executable
sudo rm /usr/local/bin/gsai

# Or if using uv
uv tool uninstall gsai

# Remove configuration and cache
rm -rf ~/.ai/gsai

# Remove from package managers
brew uninstall gsai  # Homebrew
sudo apt remove gsai # APT
```

## 🤝 Community and Support

### Q: Where can I report bugs or request features?
**A:** 
- **GitHub Issues**: [github.com/your-org/gitstart-cli/issues](https://github.com/your-org/gitstart-cli/issues)
- **Discussions**: [github.com/your-org/gitstart-cli/discussions](https://github.com/your-org/gitstart-cli/discussions)

### Q: Can I contribute to the project?
**A:** Yes! See [Contributing Guide](contributing.md) for:
- Code contributions
- Documentation improvements
- Bug reports
- Feature requests

### Q: Is there a community chat or forum?
**A:** Check the GitHub repository for:
- GitHub Discussions
- Discord server (if available)
- Community guidelines

### Q: Who maintains this project?
**A:** GitStart CoPilot CLI is maintained by GitStart AI with contributions from the open-source community.

## 📝 Still Have Questions?

1. **Check the docs**: Browse other guides in `/docs`
2. **Search issues**: Someone might have asked already
3. **Ask the community**: Use GitHub Discussions
4. **Report bugs**: Open an issue with details

**Pro tip**: The AI assistant can often help with its own usage! Try asking:
```
You: How do I configure you to use GPT-4 for coding tasks?
You: What's the best approval mode for my workflow?
You: How can I reduce my API usage costs?
```

---

**Need more help?** Check [Troubleshooting](troubleshooting.md) or [CLI Reference](cli-reference.md)