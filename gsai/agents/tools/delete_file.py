"""File deletion tool for AI Coding CLI."""

import os

from loguru import logger
from pydantic_ai import RunContext

from gsai.agents.tools.deps import FileToolDeps
from gsai.display_helpers import delete_file_description, with_progress_display
from gsai.security import SecurityError, safe_construct_path


@with_progress_display("delete_file", delete_file_description)
def delete_file(
    ctx: RunContext[FileToolDeps],
    relative_file_path: str,
) -> str:
    """
    Deletes a file at the specified path.

    This function safely deletes a file (not directories) from the repository.
    The operation requires approval unless running in full-auto mode.

    CRITICAL WARNING: File deletion is irreversible. Make sure you have backups
    before deletion.

    IMPORTANT: When specifying paths always use paths relative to the repo path.
    Examples:
    - To delete `/repo/file.txt` use `relative_file_path="file.txt"`
    - To delete `/repo/src/main.py` use `relative_file_path="src/main.py"`

    :param relative_file_path: The relative path to the file from the repository root.
    :type relative_file_path: str

    :returns: A confirmation message describing the deletion operation.
    :rtype: str
    """
    try:
        # Check approval for file deletion operation
        safe_path = ctx.deps.approval_manager.validate_file_operation(
            "delete_file", relative_file_path, f"Delete {relative_file_path}"
        )

        full_file_path = safe_construct_path(ctx.deps.repo_path, safe_path)

        # Validate that the path exists and is a file (not a directory)
        if not os.path.exists(full_file_path):
            return f"Error: File does not exist: {relative_file_path}"

        if not os.path.isfile(full_file_path):
            return f"Error: Path is not a file (directories not supported): {relative_file_path}"

        logger.info(f"Deleting file: {full_file_path}")

        # Delete the file
        os.remove(full_file_path)

        return f"File deleted successfully: {relative_file_path}"

    except SecurityError as e:
        return f"Security error: {e}"
    except FileNotFoundError:
        return f"Error: File not found: {relative_file_path}"
    except IsADirectoryError:
        return f"Error: Path is a directory, not a file: {relative_file_path}"
    except Exception as e:
        return f"Error deleting file: {e}"
