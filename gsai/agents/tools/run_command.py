"""Command execution tool for AI Coding CLI with security validation."""

import subprocess

from loguru import logger
from pydantic_ai import RunContext

from gsai.agents.tools.deps import FileToolDeps
from gsai.display_helpers import (
    run_command_description,
    with_progress_display,
)
from gsai.security import SecurityError


@with_progress_display("run_command", run_command_description)
def run_command(
    ctx: RunContext[FileToolDeps],
    command: str,
    description: str = "",
    working_directory: str | None = None,
    timeout: int = 30,
) -> str:
    """
    Execute a command line command with security validation and approval.

    This tool allows running any command line command, but ALWAYS requires approval
    regardless of the approval mode setting. This ensures maximum security for
    potentially dangerous operations.

    CRITICAL: This tool should NOT be used for code searching or file listing tasks,
    as dedicated tools already exist for those purposes:
    - Use search_for_code for searching within file contents
    - Use search_for_files for finding files by name patterns
    - Use list_files for directory listings
    - Use quick_view_file for viewing file structures

    This tool is intended for system operations, build commands, test execution,
    and other command-line utilities that require shell access.

    Args:
        ctx: The run context containing dependencies
        command: The command to execute
        description: Optional description of what the command does
        working_directory: Optional working directory override (must be within repo)
        timeout: Command timeout in seconds (default: 30)

    Returns:
        Command output or error message
    """
    try:
        # ALWAYS require approval for command execution, regardless of approval mode
        if not ctx.deps.approval_manager.request_command_approval(
            command, description, force_approval=True
        ):
            raise SecurityError(f"Command execution '{command}' denied by user")

        # Determine working directory
        if working_directory:
            # Validate working directory is within allowed bounds
            work_dir = ctx.deps.approval_manager.validate_path_within_working_dir(
                working_directory
            )
        else:
            work_dir = ctx.deps.security_context.working_directory

        logger.info(f"Executing command: {command} in directory: {work_dir}")

        # Execute the command with security constraints
        # Better Windows compatibility
        import platform
        
        # On Windows, use cmd.exe for shell commands
        if platform.system() == "Windows":
            shell_cmd = ["cmd", "/c", command]
            result = subprocess.run(
                shell_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=work_dir,
            )
        else:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=work_dir,
            )

        # Prepare output
        output_lines = []
        if result.stdout:
            output_lines.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output_lines.append(f"STDERR:\n{result.stderr}")

        output_lines.append(f"Exit code: {result.returncode}")

        output = "\n".join(output_lines)

        # Log the result
        if result.returncode == 0:
            logger.info(f"Command succeeded: {command}")
        else:
            logger.warning(
                f"Command failed with exit code {result.returncode}: {command}"
            )

        return output

    except subprocess.TimeoutExpired:
        error_msg = f"Command timed out after {timeout} seconds: {command}"
        logger.error(error_msg)
        return error_msg
    except SecurityError:
        # Re-raise security errors
        raise
    except Exception as e:
        error_msg = f"Error executing command '{command}': {e}"
        logger.error(error_msg)
        return error_msg
