"""File move tool for AI Coding CLI."""

import shutil

from loguru import logger
from pydantic_ai import RunContext

from gsai.agents.tools.deps import FileToolDeps
from gsai.display_helpers import (
    move_file_description,
    with_progress_display,
)
from gsai.security import SecurityError, safe_construct_path


def use_mv(source_path: str, destination_path: str) -> str:
    """
    Move a file using shutil.

    Args:
        source_path: Source file path
        destination_path: Destination file path

    Returns:
        Success message or error
    """
    try:
        shutil.move(source_path, destination_path)
        return f"Successfully moved {source_path} to {destination_path}"
    except Exception as e:
        return f"Error moving file: {e}"


@with_progress_display("move_file", move_file_description)
def move_file(
    ctx: RunContext[FileToolDeps],
    source_path: str,
    destination_path: str,
) -> str:
    """
    Moves or renames a file using the mv command.
    This function uses the mv command to move a file from one location to another or rename it.
    It constructs absolute paths for both source and destination using safe_construct_path
    and executes the mv command.

    CRITICAL WARNING: if you move or rename a file, any code that imports that file will need to be modified or the code will break.

    IMPORTANT: When specifying paths always use paths relative to the repo path which is: {{repo_path}}.
    Here are some examples given the repo path of /data/repos/instance-2123/client-acme-test:
    - if you want to move `/data/repos/instance-2123/client-acme-test/file.txt` to `/data/repos/instance-2123/client-acme-test/dir/file.txt`
      then use `source_path="file.txt"` and `destination_path="dir/file.txt"`
    - if you want to rename `/data/repos/instance-2123/client-acme-test/old_name.py` to `/data/repos/instance-2123/client-acme-test/new_name.py`
      then use `source_path="old_name.py"` and `destination_path="new_name.py"`

    :param source_path: The relative path to the source file from the repository root.
    :type source_path: str
    :param destination_path: The relative path to the destination file or directory from the repository root.
    :type destination_path: str

    :returns: A confirmation message describing the move operation.
    :rtype: str
    """
    # Check approval for file move operation
    try:
        # Validate both source and destination paths
        safe_source = ctx.deps.approval_manager.validate_file_operation(
            "move_file_source", source_path, f"Move {source_path} to {destination_path}"
        )
        safe_dest = ctx.deps.approval_manager.validate_file_operation(
            "move_file_destination",
            destination_path,
            f"Move {source_path} to {destination_path}",
        )

        full_source_path = safe_construct_path(ctx.deps.repo_path, safe_source)
        full_destination_path = safe_construct_path(ctx.deps.repo_path, safe_dest)

        logger.info(f"Moving file from {full_source_path} to {full_destination_path}")

        result = use_mv(full_source_path, full_destination_path)

    except SecurityError as e:
        return f"Security error: {e}"
    except Exception as e:
        return f"Error moving file: {e}"
    return result
