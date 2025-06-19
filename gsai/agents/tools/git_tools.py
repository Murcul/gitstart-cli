"""CLI-safe git operation tools with security validation."""

from pathlib import Path

from pydantic_ai import RunContext

from gsai.agents.tools.deps import WriteToolDeps
from gsai.display_helpers import git_description, with_progress_display
from gsai.security import SecurityError


@with_progress_display("git_status", git_description)
def cli_git_status(ctx: RunContext[WriteToolDeps]) -> str:
    """
    Executes the git status command and returns the repository status.

    This tool runs the equivalent of a CLI "git status" command in the context of the repository. It provides an overview of the current branch, staged changes, and working tree modifications. This is a read-only operation used for inspecting repository status.

    IMPORTANT: This command does not modify any repository data; it simply retrieves the current status.

    Args:
        ctx: The run context containing necessary dependencies to execute CLI commands.

    Returns:
        A string containing the detailed output of the git status command.

    Usage Example:
        status = cli_git_status(ctx)
    """
    try:
        # Validate that we're in a git repository within working directory
        repo_path = Path(ctx.deps.repo_path)
        working_dir = Path(ctx.deps.security_context.working_directory)

        if not repo_path.is_relative_to(working_dir):
            raise SecurityError("Repository is outside working directory")

        # Get git status
        status = ctx.deps.git_repo.git.status("--porcelain")
        if not status:
            return "Working directory clean"

        return f"Git status:\n{status}"
    except SecurityError as e:
        return f"Security error: {e}"
    except Exception as e:
        return f"Error getting git status: {e}"


@with_progress_display("git_commit", git_description)
def cli_git_commit(
    ctx: RunContext[WriteToolDeps],
    commit_message: str,
    add_all: bool = False,
) -> str:
    """
    Commits staged changes with a provided commit message using the git commit command.

    This tool performs a CLI git commit operation. It commits all currently staged changes with the specified commit message. The commit message should follow best practices and clearly describe the changes made.

    WARNING: The commit_message parameter MUST be provided. The operation will fail if it is omitted or empty.

    Args:
        ctx: The run context containing dependencies for executing Git operations.
        commit_message: A string containing the commit message that explains the changes.
        add_all: A boolean flag to optionally stage all changes before committing (default: False).

    Returns:
        A string confirming the commit operation or an error message if the commit fails.

    Usage Example:
        result = cli_git_commit(ctx, "Refactor utility functions for clarity")
    """
    try:
        # Validate command execution
        command = f"git commit -m '{commit_message}'"
        if add_all:
            command = f"git add . && {command}"

        ctx.deps.approval_manager.validate_command_execution(
            command, f"Commit changes with message: {commit_message}"
        )

        # Add files if requested
        if add_all:
            ctx.deps.git_repo.git.add(".")

        # Check if there are changes to commit
        if not ctx.deps.git_repo.is_dirty() and not ctx.deps.git_repo.untracked_files:
            return "No changes to commit"

        # Commit changes
        commit = ctx.deps.git_repo.index.commit(commit_message)
        return f"Committed changes: {commit.hexsha[:8]} - {commit_message}"
    except SecurityError as e:
        return f"Security error: {e}"
    except Exception as e:
        return f"Error committing changes: {e}"
