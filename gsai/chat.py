"""Interactive chat interface for CLI with Rich formatting."""

import asyncio
import pathlib
from typing import Any

from asyncer import asyncify
from pydantic_ai.messages import ModelMessage
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt

import gsai.config
from gsai.agents import MasterAgentDeps, master_agent
from gsai.config import CLISettings, cli_settings, config_manager
from gsai.display_helpers import ToolExecutionDisplay, tool_display_context
from gsai.repo_map import get_repo_map_for_prompt_cached, open_file
from gsai.security import ApprovalManager, create_security_context
from gsai.special import get_all_directories_in_path

console = Console()


class ChatSession:
    """Manages an interactive chat session with the AI coding assistant."""

    def __init__(
        self,
        working_directory: str,
        approval_mode: str = "suggest",
        web_search_enabled: bool = False,
        verbose: bool = False,
    ):
        self.working_directory = working_directory
        self.security_context = create_security_context(
            working_directory, approval_mode, web_search_enabled, verbose
        )
        self.approval_manager = ApprovalManager(self.security_context)
        self.session_state: dict[str, Any] = {}
        self.message_history: list[ModelMessage] = []

        self.tool_display = ToolExecutionDisplay(console)

    async def ensure_api_keys(self) -> bool:
        """Ensure API keys are configured, prompt if missing."""
        
        # Check if we have any valid API keys (non-empty strings)
        has_openai = cli_settings.OPENAI_API_KEY and cli_settings.OPENAI_API_KEY.strip()
        has_anthropic = cli_settings.ANTHROPIC_API_KEY and cli_settings.ANTHROPIC_API_KEY.strip()

        if not has_openai and not has_anthropic:
            console.print(
                Panel(
                    "[yellow]No API keys configured. You need at least one API key to use the AI assistant.[/yellow]\n\n"
                    "You can:\n"
                    "• Use the /set-api-key command to configure keys interactively\n"
                    "• Run 'gsai configure' from the command line\n"
                    "• Set environment variables OPENAI_API_KEY or ANTHROPIC_API_KEY",
                    title="API Keys Required",
                    border_style="yellow",
                )
            )
            return False
        return True

    async def prompt_for_missing_keys(self) -> None:
        """Interactively prompt for missing API keys."""

        has_openai = cli_settings.OPENAI_API_KEY and cli_settings.OPENAI_API_KEY.strip()
        has_anthropic = cli_settings.ANTHROPIC_API_KEY and cli_settings.ANTHROPIC_API_KEY.strip()

        if not has_openai:
            openai_key = Prompt.ask(
                "OpenAI API Key (leave empty to skip)",
                default="",
                show_default=False,
                password=True,
                console=console,
            )
            if openai_key.strip():
                success = config_manager.save_api_key(
                    "OPENAI_API_KEY", openai_key.strip()
                )
                if success:
                    console.print(
                        "[green]✓ OpenAI API key saved to global configuration[/green]"
                    )
                    # Reload settings to pick up the new key
                    gsai.config.cli_settings = CLISettings()
                else:
                    console.print("[red]✗ Failed to save OpenAI API key[/red]")

        if not has_anthropic:
            anthropic_key = Prompt.ask(
                "Anthropic API Key (leave empty to skip)",
                default="",
                show_default=False,
                password=True,
                console=console,
            )
            if anthropic_key.strip():
                success = config_manager.save_api_key(
                    "ANTHROPIC_API_KEY", anthropic_key.strip()
                )
                if success:
                    console.print(
                        "[green]✓ Anthropic API key saved to global configuration[/green]"
                    )
                    # Reload settings to pick up the new key
                    gsai.config.cli_settings = CLISettings()
                else:
                    console.print("[red]✗ Failed to save Anthropic API key[/red]")

    def handle_slash_command(self, command: str) -> bool:
        """Handle slash commands. Returns True if command was handled."""
        command = command.strip()
        if not command.startswith("/"):
            return False

        parts = command[1:].split()
        if not parts:
            return False

        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        if cmd == "help":
            self._show_slash_help()
        elif cmd == "config":
            self._show_config_status()
        elif cmd == "status":
            self._show_config_status()
        elif cmd == "set-api-key":
            asyncio.create_task(self._handle_set_api_key(args))
        elif cmd == "migrate-config":
            self._handle_migrate_config()
        else:
            console.print(f"[red]Unknown command: /{cmd}[/red]")
            console.print("Type /help to see available commands.")

        return True

    def _show_slash_help(self) -> None:
        """Show help for slash commands."""
        help_text = """
# Slash Commands

**Configuration Commands:**
- `/config` or `/status` - Show current configuration status
- `/set-api-key [openai|anthropic]` - Set API keys interactively
- `/migrate-config` - Migrate local .env to global configuration

**General Commands:**
- `/help` - Show this help message

**Examples:**
- `/set-api-key openai` - Set only OpenAI API key
- `/set-api-key` - Set both API keys interactively
- `/config` - View current configuration
        """
        console.print(
            Panel(Markdown(help_text), title="Slash Commands Help", border_style="blue")
        )

    def _show_config_status(self) -> None:
        """Show configuration status."""

        global_status = config_manager.get_config_status()

        status_text = f"""
**Global Configuration:**
- Directory: `{global_status["global_config_dir"]}`
- Config File Exists: {"✓ Yes" if global_status["global_config_exists"] == "True" else "✗ No"}

**API Keys:**
- OpenAI: {"✓ Configured" if cli_settings.OPENAI_API_KEY else "✗ Not configured"}
- Anthropic: {"✓ Configured" if cli_settings.ANTHROPIC_API_KEY else "✗ Not configured"}

**Session Settings:**
- Working Directory: `{self.security_context.working_directory}`
- Approval Mode: `{self.security_context.approval_mode}`
- Web Search: {"Enabled" if self.security_context.web_search_enabled else "Disabled"}
        """

        # Add agent model configurations
        agent_models_info: str = global_status.get("agent_models", "Not configured")
        if agent_models_info and agent_models_info != "Not configured":
            status_text += f"\n**Agent Models:** {agent_models_info}\n"

        console.print(
            Panel(
                Markdown(status_text), title="Configuration Status", border_style="cyan"
            )
        )

    async def _handle_set_api_key(self, args: list[str]) -> None:
        """Handle setting API keys."""
        if args and args[0].lower() == "openai":
            # Set only OpenAI key
            openai_key = Prompt.ask("OpenAI API Key", password=True, console=console)
            if openai_key.strip():
                success = config_manager.save_api_key(
                    "OPENAI_API_KEY", openai_key.strip()
                )
                if success:
                    console.print("[green]✓ OpenAI API key saved[/green]")
                    gsai.config.cli_settings = CLISettings()
                else:
                    console.print("[red]✗ Failed to save OpenAI API key[/red]")
        elif args and args[0].lower() == "anthropic":
            # Set only Anthropic key
            anthropic_key = Prompt.ask(
                "Anthropic API Key", password=True, console=console
            )
            if anthropic_key.strip():
                success = config_manager.save_api_key(
                    "ANTHROPIC_API_KEY", anthropic_key.strip()
                )
                if success:
                    console.print("[green]✓ Anthropic API key saved[/green]")
                    gsai.config.cli_settings = CLISettings()
                else:
                    console.print("[red]✗ Failed to save Anthropic API key[/red]")
        else:
            # Set both keys interactively
            await self.prompt_for_missing_keys()

    def _handle_migrate_config(self) -> None:
        """Handle migrating local config to global."""
        local_env = pathlib.Path(self.security_context.working_directory) / ".env"
        if local_env.exists():
            success = config_manager.migrate_local_to_global(local_env)
            if success:
                console.print(
                    "[green]✓ Successfully migrated local configuration to global[/green]"
                )
                gsai.config.cli_settings = CLISettings()
            else:
                console.print("[yellow]No API keys found in local .env file[/yellow]")
        else:
            console.print("[yellow]No local .env file found to migrate[/yellow]")

    def display_welcome(self) -> None:
        """Display welcome message and session information."""
        welcome_text = rf"""


# Welcome to GitStart AI CLI (gsai)

```

    ██████╗ ██╗████████╗███████╗████████╗ █████╗ ██████╗ ████████╗
   ██╔════╝ ██║╚══██╔══╝██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝
   ██║  ███╗██║   ██║   ███████╗   ██║   ███████║██████╔╝   ██║
   ██║   ██║██║   ██║   ╚════██║   ██║   ██╔══██║██╔══██╗   ██║
   ╚██████╔╝██║   ██║   ███████║   ██║   ██║  ██║██║  ██║   ██║
    ╚═════╝ ╚═╝   ╚═╝   ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝

```

**Working Directory:** `{self.security_context.working_directory}`
**Approval Mode:** `{self.security_context.approval_mode}`
**Web Search:** `{"Enabled" if self.security_context.web_search_enabled else "Disabled"}`
**Verbose Mode:** `{"Enabled" if self.security_context.verbose else "Disabled"}`

## Available Commands:
- Ask questions about your codebase
- Request code modifications or new features
- Get implementation plans for complex tasks
- Perform git operations
- Type `quit` or `exit` to end the session
- Type `help` for more information
- Type `/help` for slash commands (configuration, etc.)

## Approval Modes:
- **suggest**: Read-only mode, requires approval for all changes
- **auto-edit**: Can edit files, requires approval for commands
- **full-auto**: Can edit files and run commands without approval

Ready to assist with your coding tasks!
        """

        console.print(
            Panel(
                Markdown(welcome_text),
                title="GitStart AI Assistant",
                border_style="blue",
            )
        )

    def display_help(self) -> None:
        """Display help information."""
        help_text = """
# GitStart AI CLI Help

## Example Requests:

### Code Writing:
- "Add a new function to calculate fibonacci numbers"
- "Refactor the user authentication module"
- "Fix the bug in the payment processing code"
- "Create a new API endpoint for user registration"

### Questions & Analysis:
- "How does the authentication system work?"
- "What are the main components of this project?"
- "Explain the database schema"
- "What dependencies does this project use?"

### Git Operations:
- "Check git status"
- "Commit the current changes"
- "Show me the git log"

### Implementation Planning:
- "Create an implementation plan for adding user roles"
- "Plan the migration to a new database"
- "Design the architecture for a new feature"

## Security Features:
- All operations are restricted to your working directory
- File modifications require approval based on your approval mode
- Command execution is controlled by security settings
        """

        console.print(Panel(Markdown(help_text), title="Help", border_style="green"))

    def display_ai_response(self, response: str, task_type: str = "general") -> None:
        """Display AI response with appropriate formatting."""
        # Determine panel style based on task type
        style_map = {
            "code_writing": "yellow",
            "question_answering": "blue",
            "git_operations": "green",
            "implementation_planning": "magenta",
            "general": "white",
        }

        style = style_map.get(task_type, "white")
        title = task_type.replace("_", " ").title()

        console.print(
            Panel(
                Markdown(response), title=f"AI Assistant - {title}", border_style=style
            )
        )

    def display_error(self, error: str) -> None:
        """Display error message."""
        console.print(
            Panel(f"[red]Error: {error}[/red]", title="Error", border_style="red")
        )

    def display_files_changed(
        self, files_modified: list[str], files_created: list[str]
    ) -> None:
        """Display information about files that were changed."""
        if files_modified or files_created:
            changes_text = ""

            if files_created:
                changes_text += "**Files Created:**\n"
                for file in files_created:
                    changes_text += f"- `{file}`\n"
                changes_text += "\n"

            if files_modified:
                changes_text += "**Files Modified:**\n"
                for file in files_modified:
                    changes_text += f"- `{file}`\n"

            console.print(
                Panel(Markdown(changes_text), title="File Changes", border_style="cyan")
            )

    async def process_user_input(self, user_input: str) -> bool:
        """Process user input and return whether to continue the session."""
        # Handle special commands
        if user_input.lower() in ["quit", "exit"]:
            console.print("[yellow]Goodbye![/yellow]")
            return False

        if user_input.lower() == "help":
            self.display_help()
            return True

        # Handle slash commands
        if self.handle_slash_command(user_input):
            return True

        # Check if API keys are configured before processing AI requests
        if not await self.ensure_api_keys():
            return True

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                _task = progress.add_task("Processing your request...", total=None)

                # Set progress context in approval manager for potential pausing
                self.approval_manager.set_progress_context(progress)
                with tool_display_context(self.tool_display):
                    # Create agent dependencies
                    deps = MasterAgentDeps(
                        message_history=self.message_history,
                        repo_path=self.security_context.working_directory,
                        security_context=self.security_context,
                        approval_manager=self.approval_manager,
                        session_state=self.session_state,
                        cache={},
                        thought_history=[],
                        branches={},
                    )
                    # Run the master agent
                    result = await master_agent.run(
                        user_input, deps=deps, message_history=self.message_history
                    )
                    # Add to conversation history
                    self.message_history.extend(result.new_messages())

                # Display the response
                self.display_ai_response(result.output.response)

                # Display file changes if any
                self.display_files_changed(
                    result.output.files_modified, result.output.files_created
                )

        except Exception as e:
            self.display_error(str(e))

        return True

    async def start_interactive_session(self) -> None:
        """Start the interactive chat session."""
        self.display_welcome()

        # Check for API keys and offer to configure if missing
        has_openai = cli_settings.OPENAI_API_KEY and cli_settings.OPENAI_API_KEY.strip()
        has_anthropic = cli_settings.ANTHROPIC_API_KEY and cli_settings.ANTHROPIC_API_KEY.strip()

        if not has_openai and not has_anthropic:
            # Check if this is a development environment or production build
            try:
                from gsai.build_config import EMBEDDED_OPENAI_API_KEY, EMBEDDED_ANTHROPIC_API_KEY
                is_built_version = bool(EMBEDDED_OPENAI_API_KEY or EMBEDDED_ANTHROPIC_API_KEY)
            except ImportError:
                is_built_version = False
            
            if is_built_version:
                # Production build but keys are still empty - this shouldn't happen
                message = "[red]Build configuration issue: API keys not properly embedded during build.[/red]\n\n" \
                         "This version was built with GitHub Actions but API keys are missing.\n" \
                         "Please contact the distributor or configure your own keys."
            else:
                # Development environment
                message = "[yellow]No API keys configured.[/yellow]\n\n" \
                         "For development, you can:\n" \
                         "• Configure keys now (saves to ~/.ai/gsai/.env)\n" \
                         "• Set environment variables OPENAI_API_KEY or ANTHROPIC_API_KEY\n" \
                         "• Build the application with embedded keys via GitHub Actions"
            
            console.print(
                Panel(
                    message,
                    title="API Keys Required",
                    border_style="yellow",
                )
            )
            setup_now = Prompt.ask(
                "Configure API keys now?",
                choices=["y", "n"],
                default="y",
                console=console,
            )
            if setup_now.lower() == "y":
                await self.prompt_for_missing_keys()
            else:
                console.print("\n[blue]💡 Quick setup:[/blue]")
                console.print("  [white]gsai configure[/white]  - Interactive configuration")
                console.print("  [white]export OPENAI_API_KEY='your-key'[/white]  - Environment variable")
                console.print("  [white]/set-api-key[/white]  - Set keys during chat session")
        else:
            # Show which API keys are available
            available_keys = []
            if has_openai:
                available_keys.append("OpenAI")
            if has_anthropic:
                available_keys.append("Anthropic")
            
            console.print(f"[green]✓ API keys configured: {', '.join(available_keys)}[/green]")

        # Load session data without Live display (initialization only)
        console.print("🔄 Loading Repo Map...")
        repo_map = await asyncify(get_repo_map_for_prompt_cached)(
            repo_path=self.working_directory
        )

        console.print("🔄 Getting Dirs...")
        all_directories_in_repo = await asyncify(get_all_directories_in_path)(
            repo_path=self.working_directory
        )
        directory_count = len(all_directories_in_repo)
        if directory_count > 1000:
            all_directories_in_repo = sorted(
                all_directories_in_repo, key=lambda directory: directory.count("/")
            )[:1000]
            all_directories_in_repo.append(
                f"... Showing only 1000 of {directory_count} total directories"
            )

        self.session_state["repo_map"] = repo_map
        self.session_state["all_directories_in_repo"] = all_directories_in_repo
        self.session_state["memory"] = open_file(f"{self.working_directory}/GSAI.md")

        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold blue]You[/bold blue]", console=console)

                if not user_input.strip():
                    continue

                # Process input and check if we should continue
                should_continue = await self.process_user_input(user_input.strip())
                if not should_continue:
                    break

            except KeyboardInterrupt:
                console.print("\n[yellow]Session interrupted. Goodbye![/yellow]")
                break
            except EOFError:
                console.print("\n[yellow]Session ended. Goodbye![/yellow]")
                break


async def start_chat_session(
    working_directory: str,
    approval_mode: str = "suggest",
    web_search_enabled: bool = False,
    verbose: bool = False,
) -> None:
    """Start a new chat session."""
    session = ChatSession(working_directory, approval_mode, web_search_enabled, verbose)
    await session.start_interactive_session()
