"""Security layer for CLI operations with path validation and approval workflows."""

import os
from pathlib import Path

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.prompt import Confirm

from gsai.config import SecurityContext
from gsai.display_helpers import DiffVisualizer

console = Console()


def safe_construct_path(abs_repo_path: str, relative_path: str) -> str:
    """
    Safely construct a path ensuring it stays within the repository bounds.

    Args:
        abs_repo_path: Absolute path to the repository root
        relative_path: Relative path to construct

    Returns:
        Safe absolute path

    Raises:
        ValueError: If the path would escape the repository bounds
    """
    # Check if relative_path is absolute
    if os.path.isabs(relative_path):
        # If it is, then we need to ensure that it starts with the repo path
        if not relative_path.startswith(abs_repo_path):
            raise ValueError(
                f"Absolute path must start with the repo path: {abs_repo_path}"
            )
        return relative_path
    # Join the paths
    return os.path.normpath(os.path.join(abs_repo_path, relative_path))


class SecurityError(Exception):
    """Raised when a security violation is detected."""

    pass


class ApprovalManager:
    """Manages user approval workflows based on security context."""

    def __init__(self, security_context: SecurityContext):
        self.security_context = security_context
        self._progress_context: Progress | None = None

    def set_progress_context(self, progress_context: Progress | None) -> None:
        """Set the active progress context for pausing during approvals."""
        self._progress_context = progress_context

    def clear_progress_context(self) -> None:
        """Clear the progress context reference."""
        self._progress_context = None

    def request_file_operation_approval(
        self,
        operation: str,
        file_path: str,
        details: str = "",
        original_content: str | None = None,
        new_content: str | None = None,
    ) -> bool:
        """Request user approval for file operations."""
        if not self.security_context.requires_approval_for_files():
            return True

        # Pause progress spinner if one is active
        progress_was_active = False
        if self._progress_context is not None:
            try:
                self._progress_context.stop()
                progress_was_active = True
            except Exception:
                # If stopping fails, continue anyway
                pass

        try:
            # Display basic operation info
            console.print(
                Panel(
                    f"[bold yellow]File Operation Approval Required[/bold yellow]\n\n"
                    f"Operation: {operation}\n"
                    f"File: {file_path}\n"
                    f"Details: {details}",
                    title="Security Check",
                    border_style="yellow",
                )
            )

            # Show diff if both original and new content are provided
            if original_content is not None and new_content is not None:
                filename = os.path.basename(file_path)
                DiffVisualizer.show_file_diff(original_content, new_content, filename)

            return Confirm.ask("  Do you approve this file operation?")
        finally:
            # Resume progress spinner if it was active
            if progress_was_active and self._progress_context is not None:
                try:
                    self._progress_context.start()
                except Exception:
                    # If restarting fails, continue anyway
                    pass

    def request_command_approval(
        self, command: str, description: str = "", force_approval: bool = False
    ) -> bool:
        """Request user approval for command execution."""
        # If force_approval is True, always request approval regardless of approval mode
        if (
            not force_approval
            and not self.security_context.requires_approval_for_commands()
        ):
            return True

        # Pause progress spinner if one is active
        progress_was_active = False
        if self._progress_context is not None:
            try:
                self._progress_context.stop()
                progress_was_active = True
            except Exception:
                # If stopping fails, continue anyway
                pass

        try:
            approval_reason = "Command Execution Approval Required"
            if force_approval:
                approval_reason = "MANDATORY Command Execution Approval"

            console.print(
                Panel(
                    f"[bold red]{approval_reason}[/bold red]\n\n"
                    f"Command: {command}\n"
                    f"Description: {description}",
                    title="Security Check",
                    border_style="red",
                )
            )

            return Confirm.ask("  Do you approve this command execution?")
        finally:
            # Resume progress spinner if it was active
            if progress_was_active and self._progress_context is not None:
                try:
                    self._progress_context.start()
                except Exception:
                    # If restarting fails, continue anyway
                    pass

    def validate_path_within_working_dir(self, file_path: str) -> str:
        """Validate that file path is within working directory and return safe path."""
        try:
            safe_path = safe_construct_path(
                self.security_context.working_directory, file_path
            )

            # Additional check to ensure the resolved path is within working directory
            abs_file_path = Path(safe_path).resolve()
            abs_working_dir = Path(self.security_context.working_directory).resolve()

            if not abs_file_path.is_relative_to(abs_working_dir):
                raise SecurityError(
                    f"Path '{file_path}' resolves outside working directory '{self.security_context.working_directory}'"
                )

            return safe_path
        except (ValueError, OSError) as e:
            raise SecurityError(f"Invalid path '{file_path}': {e}")

    def validate_file_operation(
        self,
        operation: str,
        file_path: str,
        details: str = "",
        original_content: str | None = None,
        new_content: str | None = None,
    ) -> str:
        """Validate and potentially approve a file operation."""
        # First validate the path
        safe_path = self.validate_path_within_working_dir(file_path)

        # Check if file operations are allowed or require approval
        if not self.security_context.can_edit_files():
            if self.security_context.approval_mode == "suggest":
                # In suggest mode, we can still proceed with approval
                if not self.request_file_operation_approval(
                    operation, safe_path, details, original_content, new_content
                ):
                    raise SecurityError(f"File operation '{operation}' denied by user")
            else:
                raise SecurityError(
                    "File operations not allowed in current approval mode"
                )
        elif self.security_context.requires_approval_for_files():
            # Only request approval if we haven't already done so above
            if not self.request_file_operation_approval(
                operation, safe_path, details, original_content, new_content
            ):
                raise SecurityError(f"File operation '{operation}' denied by user")

        logger.info(f"File operation approved: {operation} on {safe_path}")
        return safe_path

    def validate_command_execution(self, command: str, description: str = "") -> bool:
        """Validate and potentially approve command execution."""
        # Check if command execution is allowed or requires approval
        if not self.security_context.can_run_commands():
            if self.security_context.requires_approval_for_commands():
                # Request approval even if not normally allowed
                if not self.request_command_approval(command, description):
                    raise SecurityError(f"Command execution '{command}' denied by user")
            else:
                raise SecurityError(
                    "Command execution not allowed in current approval mode"
                )
        elif self.security_context.requires_approval_for_commands():
            # Only request approval if we haven't already done so above
            if not self.request_command_approval(command, description):
                raise SecurityError(f"Command execution '{command}' denied by user")

        logger.info(f"Command execution approved: {command}")
        return True


def validate_working_directory(directory: str) -> str:
    """Validate and normalize working directory path."""
    try:
        abs_dir = os.path.abspath(directory)
        if not os.path.exists(abs_dir):
            raise SecurityError(f"Working directory does not exist: {abs_dir}")
        if not os.path.isdir(abs_dir):
            raise SecurityError(f"Working directory is not a directory: {abs_dir}")
        return abs_dir
    except OSError as e:
        raise SecurityError(f"Invalid working directory '{directory}': {e}")


def create_security_context(
    working_directory: str,
    approval_mode: str,
    web_search_enabled: bool = False,
    verbose: bool = False,
) -> SecurityContext:
    """Create and validate security context."""
    validated_dir = validate_working_directory(working_directory)

    return SecurityContext(
        working_directory=validated_dir,
        approval_mode=approval_mode,  # type: ignore
        web_search_enabled=web_search_enabled,
        verbose=verbose,
    )
