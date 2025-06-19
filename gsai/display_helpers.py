"""Display helpers for tool execution progress and visual feedback."""

import contextvars
import difflib
import functools
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any, TypeVar

from loguru import logger
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

F = TypeVar("F", bound=Callable[..., Any])

# Context variable for async-safe display context propagation
_display_context: contextvars.ContextVar["ToolExecutionDisplay | None"] = (
    contextvars.ContextVar("tool_display", default=None)
)


class DiffVisualizer:
    """Handles generation and display of colorized file diffs."""

    @staticmethod
    def generate_diff(
        original_content: str, new_content: str, filename: str = "file"
    ) -> list[str]:
        """Generate unified diff between original and new content."""
        original_lines = original_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)

        diff = list(
            difflib.unified_diff(
                original_lines,
                new_lines,
                fromfile=f"a/{filename}",
                tofile=f"b/{filename}",
                lineterm="",
            )
        )

        return diff

    @staticmethod
    def display_diff(diff_lines: list[str], max_lines: int = 50) -> None:
        """Display colorized diff in the terminal."""
        console = Console()
        if not diff_lines:
            console.print("[dim]No changes detected[/dim]")
            return

        # Skip the diff headers (first 2 lines)
        content_lines = diff_lines[2:] if len(diff_lines) > 2 else diff_lines

        # Truncate if too long
        if len(content_lines) > max_lines:
            content_lines = content_lines[:max_lines]
            truncated = True
        else:
            truncated = False

        # Create colorized diff display with minimal line spacing
        diff_text = Text()

        for line in content_lines:
            # Remove any trailing whitespace to ensure consistent spacing
            line = line.rstrip()

            if line.startswith("+") and not line.startswith("+++"):
                # Addition (green)
                diff_text.append(line + "\n", style="bright_green")
            elif line.startswith("-") and not line.startswith("---"):
                # Deletion (red)
                diff_text.append(line + "\n", style="bright_red")
            elif line.startswith("@@"):
                # Hunk header (cyan)
                diff_text.append(line + "\n", style="bright_cyan")
            else:
                # Context (default)
                diff_text.append(line + "\n", style="dim")

        # Remove the last newline to prevent extra spacing at the end
        if diff_text.plain.endswith("\n"):
            diff_text = Text(diff_text.plain[:-1])
            # Re-apply styling
            diff_text = Text()
            for line in content_lines:
                line = line.rstrip()
                if line.startswith("+") and not line.startswith("+++"):
                    diff_text.append(line, style="bright_green")
                elif line.startswith("-") and not line.startswith("---"):
                    diff_text.append(line, style="bright_red")
                elif line.startswith("@@"):
                    diff_text.append(line, style="bright_cyan")
                else:
                    diff_text.append(line, style="dim")
                # Add newline between lines but not after the last one
                if line != content_lines[-1].rstrip():
                    diff_text.append("\n")

        # Display in a panel
        panel_content = diff_text
        if truncated:
            panel_content.append(f"\n[dim]... (showing first {max_lines} lines)[/dim]")

        console.print(
            Panel(
                panel_content,
                title="[bold blue]Proposed Changes[/bold blue]",
                border_style="blue",
                expand=True,
                padding=(0, 1),
            )
        )

    @classmethod
    def show_file_diff(
        cls, original_content: str, new_content: str, filename: str = "file"
    ) -> None:
        """Show a visual diff between original and new file content."""
        diff_lines = cls.generate_diff(original_content, new_content, filename)
        cls.display_diff(diff_lines)


class ToolExecutionDisplay:
    """Manages visual feedback for tool execution in the CLI."""

    def __init__(self, console: Console):
        self.console = console
        self._tool_history: list[tuple[str, str]] = []  # (tool_name, status)

    @contextmanager
    def show_tool_execution(
        self, tool_name: str, description: str = "", is_agentic_tool: bool = False
    ) -> Generator["ToolExecutionDisplay", Any, None]:
        """Context manager to show tool execution with status indicator."""
        # Format tool name for display
        display_name = tool_name.replace("_", " ").title()
        padding = "  "
        if is_agentic_tool:
            # Print start message
            start_msg = f"🔧 [bold blue]{display_name}[/bold blue]"
            if description:
                start_msg += f" - {description}"
            self.console.print(start_msg)
            padding = ""

        try:
            yield self

            # Print success message
            success_msg = f"{padding}{_get_tool_icon(tool_name)} [bold green]{display_name} Complete[/bold green]"
            if description:
                success_msg += f" - {description}"
            self.console.print(success_msg)
            self._tool_history.append((tool_name, "completed"))

        except Exception:
            # Print error message
            error_msg = f"{padding}❌ [bold red]{display_name} Failed[/bold red]"
            if description:
                error_msg += f" - {description}"
            self.console.print(error_msg)
            self._tool_history.append((tool_name, "failed"))
            raise

    def show_markdown_result(self, result_data: Any, agent_type: str) -> None:
        """Display markdown results from delegation agents."""
        try:
            content = self._format_agent_result(result_data, agent_type)
            if content:
                title = self._get_agent_result_title(agent_type)
                panel = Panel(
                    Markdown(content), title=title, border_style="green", padding=(1, 2)
                )
                self.console.print(panel)
        except Exception as e:
            logger.warning(f"Failed to display markdown result for {agent_type}: {e}")

    def _format_agent_result(self, output: Any, agent_type: str) -> str:
        """Format agent output based on agent type."""
        if agent_type == "ticket":
            return self._format_ticket_result(output)
        elif agent_type == "implementation_plan":
            return self._format_implementation_plan_result(output)
        elif agent_type == "research":
            return self._format_research_result(output)
        return ""

    def _format_ticket_result(self, output: Any) -> str:
        """Format ticket writing agent output."""
        content = ""
        if hasattr(output, "ticket_title") and output.ticket_title:
            content += f"# {output.ticket_title}\n\n"
        if hasattr(output, "ticket_description") and output.ticket_description:
            content += output.ticket_description
        return content

    def _format_implementation_plan_result(self, output: Any) -> str:
        """Format implementation planning agent output."""
        if hasattr(output, "implementation_plan") and output.implementation_plan:
            return output.implementation_plan
        return ""

    def _format_research_result(self, output: Any) -> str:
        """Format research agent output."""
        if hasattr(output, "research_document") and output.research_document:
            return output.research_document
        return ""

    def _get_agent_result_title(self, agent_type: str) -> str:
        """Get appropriate title for agent result panel."""
        titles = {
            "ticket": "🎫 Ticket Created",
            "implementation_plan": "📋 Implementation Plan",
            "research": "🔬 Research Results",
        }
        return titles.get(agent_type, "📄 Agent Result")


@contextmanager
def tool_display_context(display: "ToolExecutionDisplay") -> Generator[None, Any, None]:
    """Context manager to set the tool display for the current context."""
    token = _display_context.set(display)
    try:
        yield
    finally:
        _display_context.reset(token)


def get_current_display() -> "ToolExecutionDisplay | None":
    """Get the current tool display instance."""
    display = _display_context.get()
    logger.info(f"Current display context: {display}")
    return display


def with_progress_display(
    tool_name: str,
    description: str | Callable[..., str] = "",
    is_agentic_tool: bool = False,
) -> Callable[[F], F]:
    """Decorator to add progress display to tool functions.

    Args:
        tool_name: Name of the tool for display purposes
        description: Description to show during execution (can be a string or callable that generates description from args)
        is_agentic_tool: If True, show call and result.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            display = get_current_display()
            logger.info(f"display: {display}")
            # If no display context or this tool shouldn't show progress, run normally
            if not display:
                return func(*args, **kwargs)

            # Generate description if it's a callable
            try:
                if callable(description):
                    desc = description(*args, **kwargs)
                else:
                    desc = description
            except Exception:
                # Fallback to tool name if description generation fails
                desc = tool_name.replace("_", " ").title()

            # Truncate very long descriptions
            if len(desc) > 80:
                desc = desc[:77] + "..."

            # Run with progress display
            with display.show_tool_execution(tool_name, desc, is_agentic_tool):
                return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def with_progress_display_async(
    tool_name: str,
    description: str | Callable[..., str] = "",
    is_agentic_tool: bool = False,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Async version of the progress display decorator."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            display = get_current_display()

            # If no display context or this tool shouldn't show progress, run normally
            if not display:
                return await func(*args, **kwargs)

            # Generate description if it's a callable
            try:
                if callable(description):
                    desc = description(*args, **kwargs)
                else:
                    desc = description
            except Exception:
                # Fallback to tool name if description generation fails
                desc = tool_name.replace("_", " ").title()

            # Truncate very long descriptions
            if len(desc) > 80:
                desc = desc[:77] + "..."

            # Run with progress display
            with display.show_tool_execution(tool_name, desc, is_agentic_tool):
                return await func(*args, **kwargs)

        return wrapper

    return decorator


# Description generator functions
def view_file_description(*args: Any, **kwargs: Any) -> str:
    """Generate description for view_file operations."""
    if len(args) >= 2:  # ctx, relative_file_path
        return f"Reading {args[1]}"
    elif "relative_file_path" in kwargs:
        return f"Reading {kwargs['relative_file_path']}"
    return "Reading file"


def search_code_description(*args: Any, **kwargs: Any) -> str:
    """Generate description for search_for_code operations."""
    pattern = ""
    path = ""

    if len(args) >= 2:  # ctx, pattern
        pattern = args[1]
    elif "pattern" in kwargs:
        pattern = kwargs["pattern"]

    if len(args) >= 4:  # ctx, pattern, case_sensitive, relative_path
        path = args[3]
    elif "relative_path" in kwargs:
        path = kwargs["relative_path"]

    if pattern and path and path != ".":
        return f"Searching '{pattern}' in {path}"
    elif pattern:
        return f"Searching '{pattern}'"
    return "Searching code"


def run_command_description(*args: Any, **kwargs: Any) -> str:
    """Generate description for run_command operations."""
    if len(args) >= 2:  # ctx, command
        command = args[1]
    elif "command" in kwargs:
        command = kwargs["command"]
    else:
        return "Running command"

    # Truncate very long commands
    if len(command) > 50:
        command = command[:47] + "..."
    return f"Running: {command}"


def str_replace_description(*args: Any, **kwargs: Any) -> str:
    """Generate description for str_replace operations."""
    if len(args) >= 2:  # ctx, relative_file_path
        return f"Editing {args[1]}"
    elif "relative_file_path" in kwargs:
        return f"Editing {kwargs['relative_file_path']}"
    return "Editing file"


def overwrite_file_description(*args: Any, **kwargs: Any) -> str:
    """Generate description for overwrite_file operations."""
    if len(args) >= 2:  # ctx, relative_file_path
        return f"Overwriting {args[1]}"
    elif "relative_file_path" in kwargs:
        return f"Overwriting {kwargs['relative_file_path']}"
    return "Overwriting file"


def move_file_description(*args: Any, **kwargs: Any) -> str:
    """Generate description for move_file operations."""
    if len(args) >= 3:  # ctx, source_path, destination_path
        return f"Moving {args[1]} → {args[2]}"
    elif "source_path" in kwargs and "destination_path" in kwargs:
        return f"Moving {kwargs['source_path']} → {kwargs['destination_path']}"
    return "Moving file"


def delete_file_description(*args: Any, **kwargs: Any) -> str:
    """Generate description for delete_file operations."""
    if len(args) >= 2:  # ctx, relative_file_path
        return f"Deleting {args[1]}"
    elif "relative_file_path" in kwargs:
        return f"Deleting {kwargs['relative_file_path']}"
    return "Deleting file"


def search_files_description(*args: Any, **kwargs: Any) -> str:
    """Generate description for search_for_files operations."""
    if len(args) >= 2:  # ctx, glob_pattern
        return f"Finding files: {args[1]}"
    elif "glob_pattern" in kwargs:
        return f"Finding files: {kwargs['glob_pattern']}"
    return "Finding files"


def quick_view_description(*args: Any, **kwargs: Any) -> str:
    """Generate description for quick_view_file operations."""
    if len(args) >= 2:  # ctx, relative_path
        return f"Analyzing {args[1]}"
    elif "relative_path" in kwargs:
        return f"Analyzing {kwargs['relative_path']}"
    return "Analyzing file structure"


def lint_description(*args: Any, **kwargs: Any) -> str:
    """Generate description for lint_source_code operations."""
    if len(args) >= 2:  # ctx, relative_file_path
        return f"Linting {args[1]}"
    elif "relative_file_path" in kwargs:
        return f"Linting {kwargs['relative_file_path']}"
    return "Linting code"


def git_description(*args: Any, **kwargs: Any) -> str:
    """Generate description for git operations."""
    if len(args) >= 2:  # ctx, operation
        operation = args[1]
        if operation == "status":
            return "Checking git status"
        elif operation == "add":
            return "Adding files to git"
        elif operation == "commit":
            return "Committing changes"
        elif operation == "log":
            return "Viewing git log"
        else:
            return f"Git: {operation}"
    return "Git operation"


def _get_tool_icon(tool_name: str) -> str:
    """Get appropriate icon for tool based on its type."""
    tool_icons = {
        "view_file": "📄",
        "search_for_code": "🔍",
        "search_for_files": "📁",
        "run_command": "⚙️",
        "git_tools": "🔀",
        "lint_source_code": "🔧",
        "overwrite_file": "📝",
        "str_replace": "✏️",
        "move_file": "📦",
        "delete_file": "🗑️",
        "quick_view_file": "⚡",
        "list_files": "📋",
        "save_to_memory": "💾",
        "sequential_thinking": "🧠",
        "expert": "🎓",
        "web_navigation": "🌐",
        "web_search": "🔎",
        "extract_relevant_context_from_url": "📖",
        # Delegation tools
        "delegate_to_code_writing_agent": "🧠",
        "delegate_to_question_answering_agent": "❓",
        "delegate_to_git_operations_agent": "🔀",
        "delegate_to_implementation_planning_agent": "📋",
        "delegate_to_research_agent": "🔬",
        "delegate_to_ticket_writing_agent": "🎫",
    }
    return tool_icons.get(tool_name, "✅")
