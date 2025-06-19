"""File viewing tool for AI Coding CLI."""

from loguru import logger
from pydantic_ai import RunContext

from gsai.agents.tools.deps import CodebaseDeps
from gsai.display_helpers import (
    view_file_description,
    with_progress_display,
)
from gsai.security import SecurityError, safe_construct_path


def open_file(file_path: str) -> str:
    """
    Opens and reads the content of a file from a specified repository path.

    Args:
        file_path: The absolute path to the file from the repository root.

    Returns:
        The content of the file if found, "File not found" if the file doesn't exist.
    """
    try:
        with open(file_path) as f:
            return f.read()
    except FileNotFoundError:
        return "File not found"
    except UnicodeDecodeError as error:
        # fallback to a lossy but safe read
        logger.warning(f"Decode Error Ignored: {file_path} - {error}")
        with open(file_path, encoding="utf-8", errors="replace") as f:
            return f.read()


@with_progress_display("view_file", view_file_description)
def view_file(ctx: RunContext[CodebaseDeps], relative_file_path: str) -> str:
    """
    Reads and returns the content of a file located within the repository.

    IMPORTANT: Only use this when you absolutely need to see the entire contents of a file, other wise:
    - Use quick_view_file if you only need to see function and class signatures.
    - Use search_for_code if you just need to see definitions and implementations of a certain function or class or variable


    The function constructs the absolute file path from the provided relative path (relative to the repository root) and then reads the file's contents.

    IMPORTANT: When specifying paths always use paths relative to the repo path which is: {{repo_path}}.
    Here are some exmaples given the repo path of /data/repos/instance-2123/client-acme-test:
    - if you want to view, modify, or create `/data/repos/instance-2123/client-acme-test/Dockerfile` then use `Dockerfile` as the path
    - if you want to view, modify, or create `/data/repos/instance-2123/client-acme-test/app/main.py` then use `app/main.py` as the path
    - if you want to view, modify, or create `/data/repos/instance-2123/client-acme-test/app/components/CoolComp.tsx` then use `app/components/CoolComp.tsx` as the path

    :param relative_file_path: The relative path to the target file from the repository root.
    :type relative_file_path: str
    :returns: A string with the file content if the file is found, or an error message indicating that the file was not found.
    :rtype: str
    """
    # Check approval for file read operation
    try:
        safe_path = ctx.deps.approval_manager.validate_path_within_working_dir(
            relative_file_path
        )

        full_file_path = safe_construct_path(ctx.deps.repo_path, safe_path)

        logger.info(f"Opening file at {full_file_path}")
        return open_file(full_file_path)
    except SecurityError as e:
        return f"Security error: {e}"
    except Exception as e:
        return f"Error viewing file: {e}"
