"""Main CLI application using Typer."""

import asyncio
import importlib.metadata
import os
import pathlib
from importlib.metadata import PackageNotFoundError
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from gsai.chat import start_chat_session
from gsai.config import cli_settings, config_manager, configure_logging
from gsai.security import SecurityError, validate_working_directory

app = typer.Typer(
    name="gsai",
    help="GitStart AI CLI - Interactive AI coding assistance",
    rich_markup_mode="rich",
)


console = Console()


def get_version() -> str:
    """Get the package version from metadata."""
    try:
        return importlib.metadata.version("gsai")
    except PackageNotFoundError:
        return "unknown"


@app.command()
def chat(
    working_dir: Annotated[
        str | None,
        typer.Option(
            "--working-dir",
            "-w",
            help="Working directory for CLI operations (defaults to current directory)",
        ),
    ] = None,
    approval_mode: Annotated[
        str,
        typer.Option(
            "--approval-mode",
            "-a",
            help="Approval mode: suggest (read-only), auto-edit (can edit files), full-auto (can edit and run commands)",
        ),
    ] = "suggest",
    web_search: Annotated[
        bool, typer.Option("--web-search", help="Enable web search for AI agents")
    ] = False,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Enable verbose logging and output")
    ] = False,
) -> None:
    """Start an interactive AI coding session."""
    try:
        # Configure logging based on verbose flag
        configure_logging(verbose)

        # Use current directory if not specified
        if working_dir is None:
            working_dir = os.getcwd()

        # Validate working directory
        validated_dir = validate_working_directory(working_dir)

        # Validate approval mode
        if approval_mode not in ["suggest", "auto-edit", "full-auto"]:
            console.print(
                "[red]Error: Invalid approval mode. Must be one of: suggest, auto-edit, full-auto[/red]"
            )
            raise typer.Exit(1)

        # Start the chat session
        asyncio.run(
            start_chat_session(validated_dir, approval_mode, web_search, verbose)
        )

    except SecurityError as e:
        console.print(f"[red]Security Error: {e}[/red]")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Session interrupted.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def configure(
    openai_key: Annotated[
        str | None,
        typer.Option("--openai-key", help="OpenAI API Key"),
    ] = None,
    anthropic_key: Annotated[
        str | None,
        typer.Option("--anthropic-key", help="Anthropic API Key"),
    ] = None,
    global_config: Annotated[
        bool,
        typer.Option("--global", help="Save to global configuration (default)"),
    ] = True,
    migrate: Annotated[
        bool,
        typer.Option("--migrate", help="Migrate local .env to global configuration"),
    ] = False,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Enable verbose logging and output")
    ] = False,
) -> None:
    """Configure API keys and save to global configuration."""
    try:
        # Configure logging based on verbose flag
        configure_logging(verbose)

        # Handle migration first
        if migrate:
            local_env = os.path.join(os.getcwd(), ".env")
            if os.path.exists(local_env):
                success = config_manager.migrate_local_to_global(
                    pathlib.Path(local_env)
                )
                if success:
                    console.print(
                        "[green]✓ Successfully migrated local configuration to global[/green]"
                    )
                else:
                    console.print(
                        "[yellow]No API keys found in local .env file[/yellow]"
                    )
            else:
                console.print("[yellow]No local .env file found to migrate[/yellow]")
            return

        # Prompt for keys if not provided via command line
        if openai_key is None:
            openai_key = typer.prompt(
                "OpenAI API Key (leave empty to skip)",
                default="",
                show_default=False,
                hide_input=True,
            )

        if anthropic_key is None:
            anthropic_key = typer.prompt(
                "Anthropic API Key (leave empty to skip)",
                default="",
                show_default=False,
                hide_input=True,
            )

        config_info: list[str] = []

        # Handle API keys
        if openai_key and openai_key.strip():
            if global_config:
                success = config_manager.save_api_key(
                    "OPENAI_API_KEY", openai_key.strip()
                )
                if success:
                    config_info.append("✓ OpenAI API key saved to global configuration")
                else:
                    config_info.append("✗ Failed to save OpenAI API key")
            else:
                os.environ["OPENAI_API_KEY"] = openai_key.strip()
                config_info.append("✓ OpenAI API key configured for this session")

        if anthropic_key and anthropic_key.strip():
            if global_config:
                success = config_manager.save_api_key(
                    "ANTHROPIC_API_KEY", anthropic_key.strip()
                )
                if success:
                    config_info.append(
                        "✓ Anthropic API key saved to global configuration"
                    )
                else:
                    config_info.append("✗ Failed to save Anthropic API key")
            else:
                os.environ["ANTHROPIC_API_KEY"] = anthropic_key.strip()
                config_info.append("✓ Anthropic API key configured for this session")

        # Display configuration summary
        if config_info:
            console.print(
                Panel(
                    "\n".join(config_info),
                    title="Configuration Updated",
                    border_style="green",
                )
            )
        else:
            console.print("[yellow]No configuration changes made.[/yellow]")

        if global_config:
            console.print(
                f"\n[dim]Configuration saved to: {config_manager.global_config_file}[/dim]"
            )
        else:
            console.print("\n[dim]Note: API keys are set for this session only.[/dim]")

    except Exception as e:
        console.print(f"[red]Error configuring settings: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def status(
    working_dir: Annotated[
        str | None,
        typer.Option(
            "--working-dir",
            "-w",
            help="Working directory to check (defaults to current directory)",
        ),
    ] = None,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Enable verbose logging and output")
    ] = False,
) -> None:
    """Show current configuration and working directory status."""
    try:
        # Configure logging based on verbose flag
        configure_logging(verbose)
        # Use current directory if not specified
        if working_dir is None:
            working_dir = os.getcwd()

        # Validate working directory
        validated_dir = validate_working_directory(working_dir)

        # Get global config status
        global_status = config_manager.get_config_status()

        # Create status table
        table = Table(title="GitStart AI CLI Status")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")

        # Working directory info
        table.add_row("Working Directory", validated_dir)
        table.add_row(
            "Directory Exists", "✓ Yes" if os.path.exists(validated_dir) else "✗ No"
        )
        table.add_row(
            "Is Git Repository",
            "✓ Yes" if os.path.exists(os.path.join(validated_dir, ".git")) else "✗ No",
        )

        # Configuration file locations
        table.add_row("Global Config Dir", global_status["global_config_dir"])
        table.add_row(
            "Global Config Exists",
            "✓ Yes" if global_status["global_config_exists"] == "True" else "✗ No",
        )

        # Local .env status
        local_env_exists = os.path.exists(os.path.join(validated_dir, ".env"))
        table.add_row("Local .env Exists", "✓ Yes" if local_env_exists else "✗ No")

        # API key status
        openai_configured = (
            "✓ Configured" if cli_settings.OPENAI_API_KEY else "✗ Not configured"
        )
        anthropic_configured = (
            "✓ Configured" if cli_settings.ANTHROPIC_API_KEY else "✗ Not configured"
        )

        table.add_row("OpenAI API Key", openai_configured)
        table.add_row("Anthropic API Key", anthropic_configured)

        # Default settings
        table.add_row("Default Approval Mode", cli_settings.approval_mode)
        table.add_row("Web Search Enabled", str(cli_settings.web_search_enabled))
        table.add_row("Verbose Mode", str(cli_settings.verbose))

        # Cache settings
        table.add_row("Cache Enabled", str(cli_settings.cache_enabled))
        table.add_row("Cache Size", global_status.get("cache_size", "0 MB"))
        table.add_row("Cache Entries", global_status.get("cache_entries", "0"))

        console.print(table)

        # Show agent model configurations
        agent_models_info: str = global_status.get("agent_models", "Not configured")
        if agent_models_info and agent_models_info != "Not configured":
            console.print(f"\n[bold]Agent Models:[/bold] {agent_models_info}")

        # Show configuration guidance
        if not cli_settings.OPENAI_API_KEY and not cli_settings.ANTHROPIC_API_KEY:
            console.print(
                "\n[yellow]⚠️  No API keys configured. Run 'gsai configure' to set up API keys.[/yellow]"
            )

        if local_env_exists and global_status["global_config_exists"] == "False":
            console.print(
                "\n[blue]💡 Consider migrating your local .env to global config: 'gsai configure --migrate'[/blue]"
            )

        # Show approval mode descriptions
        console.print("\n[bold]Approval Modes:[/bold]")
        console.print(
            "• [cyan]suggest[/cyan]: Read-only mode, requires approval for all changes"
        )
        console.print(
            "• [yellow]auto-edit[/yellow]: Can edit files, requires approval for commands"
        )
        console.print(
            "• [red]full-auto[/red]: Can edit files and run commands without approval"
        )

        # Show cache commands
        console.print("\n[bold]Cache Commands:[/bold]")
        console.print(
            "• [cyan]gsai cache-status[/cyan]: Show detailed cache information"
        )
        console.print("• [cyan]gsai cache-clear[/cyan]: Clear the repo map cache")

    except SecurityError as e:
        console.print(f"[red]Security Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("cache-status")
def cache_status(
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Enable verbose logging and output")
    ] = False,
) -> None:
    """Show cache status and statistics."""
    try:
        # Configure logging based on verbose flag
        configure_logging(verbose)

        # Get cache information
        cache_info = config_manager.get_cache_info()

        # Create cache status table
        table = Table(title="Repo Map Cache Status")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Cache Enabled", str(cli_settings.cache_enabled))
        table.add_row("Cache Directory", cache_info["cache_dir"])
        table.add_row(
            "Cache Exists", "✓ Yes" if cache_info["cache_exists"] == "True" else "✗ No"
        )
        table.add_row("Cache Size", cache_info["cache_size"])
        table.add_row("Cache Entries", cache_info["cache_entries"])
        table.add_row("TTL (days)", str(cli_settings.cache_ttl_days))
        table.add_row("Max Size (MB)", str(cli_settings.max_cache_size_mb))

        console.print(table)

        if cache_info["cache_exists"] == "False":
            console.print(
                "\n[yellow]💡 Cache will be created on first repo map generation[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]Error getting cache status: {e}[/red]")
        raise typer.Exit(1)


@app.command("cache-clear")
def cache_clear(
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Enable verbose logging and output")
    ] = False,
) -> None:
    """Clear the repo map cache."""
    try:
        # Configure logging based on verbose flag
        configure_logging(verbose)

        # Confirm with user
        confirm = typer.confirm("Are you sure you want to clear the cache?")
        if not confirm:
            console.print("[yellow]Cache clear cancelled.[/yellow]")
            return

        # Clear cache
        success = config_manager.clear_cache()
        if success:
            console.print("[green]✓ Cache cleared successfully[/green]")
        else:
            console.print("[red]✗ Failed to clear cache[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error clearing cache: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Show version information."""
    current_version = get_version()
    console.print(
        Panel(
            f"[bold]GitStart AI CLI (gsai)[/bold]\n"
            f"Version: {current_version}\n"
            "Interactive AI coding assistant with security and approval workflows",
            title="Version Info",
            border_style="blue",
        )
    )


if __name__ == "__main__":
    app()
