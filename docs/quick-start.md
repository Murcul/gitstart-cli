# Quick Start Guide

Get up and running with GitStart CoPilot CLI in 5 minutes!

## 🚀 1. Installation

If you haven't installed GitStart CoPilot CLI yet, choose the fastest method for your platform:

### Linux/macOS (One-liner)
```bash
curl -L -o gsai https://github.com/your-org/gitstart-cli/releases/latest/download/gsai-$(uname -s | tr '[:upper:]' '[:lower:]')-x86_64
chmod +x gsai && sudo mv gsai /usr/local/bin/
```

### Pre-built Executables
Download from [releases page](../releases) for your platform:
- **Linux**: `gsai-linux-x86_64`
- **macOS**: `gsai-macos-x86_64`
- **Windows**: `gsai-windows-x86_64.exe`

### Package Managers
```bash
# Homebrew (macOS/Linux)
brew install gitstart/cli/gsai

# From source with uv
git clone https://github.com/your-org/gitstart-cli.git
cd gitstart-cli && uv sync && uv tool install .
```

## ⚙️ 2. Initial Configuration

After installation, configure your API keys:

```bash
# Interactive configuration
gsai configure
```

This will prompt you for:
- **OpenAI API Key** (optional but recommended)
- **Anthropic API Key** (optional but recommended)
- **Approval Mode** (suggest/auto-edit/full-auto)
- **Web Search** (enable/disable)

### Quick Configuration with Environment Variables
```bash
export OPENAI_API_KEY="sk-your-openai-key-here"
export ANTHROPIC_API_KEY="sk-your-anthropic-key-here"
```

## ✅ 3. Verify Installation

Check that everything is working:

```bash
# Check version
gsai --version

# Check configuration status
gsai status

# View help
gsai --help
```

Expected output:
```
✓ GitStart CoPilot CLI v1.0.0
✓ OpenAI API Key: Configured
✓ Anthropic API Key: Configured
✓ Configuration: ~/.ai/gsai/.env
```

## 🎯 4. Your First AI Coding Session

Navigate to any project directory and start chatting with AI:

```bash
# Go to your project
cd /path/to/your/project

# Start interactive AI session
gsai chat
```

You'll see:
```
🤖 GitStart CoPilot CLI - AI Coding Assistant
💬 Type your coding questions or requests...

You: 
```

## 💡 5. Try These Examples

### Example 1: Code Explanation
```
You: What does this project do? Can you give me an overview?

🤖 AI: I'll analyze your project structure...
[AI provides detailed project overview]
```

### Example 2: Code Writing
```
You: Create a Python function to validate email addresses

🤖 AI: I'll create an email validation function for you...
[AI creates and explains the code]
```

### Example 3: Bug Fixing
```
You: I'm getting a "TypeError: 'NoneType' object is not subscriptable" error in line 45 of main.py

🤖 AI: Let me examine line 45 of main.py and help fix this error...
[AI analyzes and suggests fixes]
```

### Example 4: Code Review
```
You: Review my recent changes and suggest improvements

🤖 AI: I'll review your recent code changes...
[AI provides detailed code review]
```

## 🛠️ 6. Essential Commands

### Chat Commands
```bash
# Start interactive session
gsai chat

# Chat in specific directory
gsai chat --directory /path/to/project

# Chat with specific approval mode
gsai chat --approval-mode auto-edit
```

### Configuration Commands
```bash
# View current configuration
gsai status

# Reconfigure settings
gsai configure

# Show version information
gsai version
```

### Help Commands
```bash
# General help
gsai --help

# Command-specific help
gsai chat --help
gsai configure --help
```

## 🎨 7. Approval Modes Explained

Choose the right approval mode for your workflow:

### `suggest` (Safest - Default)
- AI suggests changes but doesn't make them
- You review and approve each change
- Best for: Learning, important projects, first-time use

```bash
gsai chat --approval-mode suggest
```

### `auto-edit` (Balanced)
- AI can edit files automatically
- Asks permission before running commands
- Best for: Regular development, trusted projects

```bash
gsai chat --approval-mode auto-edit
```

### `full-auto` (Fastest)
- AI can edit files and run commands without asking
- Use with caution and in safe environments
- Best for: Prototyping, experimental projects

```bash
gsai chat --approval-mode full-auto
```

## 🎪 8. Sample Workflow

Here's a typical workflow to get you started:

```bash
# 1. Navigate to your project
cd ~/my-awesome-project

# 2. Start AI session
gsai chat

# 3. Get project overview
You: Analyze this codebase and tell me what it does

# 4. Ask for specific help
You: Add error handling to the login function in auth.py

# 5. Review and iterate
You: The error handling looks good, now add logging to track failed attempts

# 6. Git integration
You: Create a commit for these authentication improvements

# 7. Exit when done
You: exit
```

## 🔧 9. Customization

### Change Approval Mode Temporarily
```bash
# Use different mode for this session
gsai chat --approval-mode auto-edit
```

### Enable Web Search
```bash
# Allow AI to search the web for help
gsai configure
# Then enable web search when prompted
```

### Verbose Mode
```bash
# See detailed operations
gsai chat --verbose
```

## 🚨 10. Safety Tips

### For First-Time Users
1. **Start with `suggest` mode** to understand what AI wants to do
2. **Use in a git repository** so you can easily revert changes
3. **Review suggestions carefully** before accepting
4. **Keep backups** of important files

### Best Practices
- Always commit your work before starting AI sessions
- Use descriptive prompts for better results
- Review AI-generated code before running
- Test changes in development environments first

## ❓ 11. Common First Questions

### "What can GitStart CoPilot do?"
- Write and edit code in any language
- Explain complex codebases
- Debug and fix errors
- Create documentation
- Suggest improvements
- Help with git operations
- Plan implementation strategies

### "How do I stop the AI session?"
Type `exit`, `quit`, or press `Ctrl+C`

### "Can I use it without API keys?"
You need at least one API key (OpenAI or Anthropic) for the AI functionality to work.

### "Is my code safe?"
- Your code stays on your machine
- API keys are stored securely in `~/.ai/gsai/.env`
- Always review changes before accepting

## 🎉 12. Next Steps

Now that you're up and running:

1. **Explore Advanced Features**: Check out [Advanced Features](advanced-features.md)
2. **Learn More Commands**: See [CLI Reference](cli-reference.md)
3. **Configuration Options**: Read [Configuration Guide](configuration.md)
4. **Real-world Examples**: Browse [Examples](examples.md)
5. **Troubleshooting**: If you have issues, see [Troubleshooting](troubleshooting.md)

## 🆘 Need Help?

- **Quick Issues**: Check [Troubleshooting](troubleshooting.md)
- **Configuration Problems**: See [Configuration Guide](configuration.md)
- **Command Reference**: Check [CLI Reference](cli-reference.md)
- **Bug Reports**: Open an issue on GitHub

---

**🎊 Congratulations!** You're now ready to supercharge your coding with AI assistance. Happy coding! 🚀