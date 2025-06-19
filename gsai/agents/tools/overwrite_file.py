"""File overwrite tool for AI Coding CLI."""

from loguru import logger
from pydantic_ai import RunContext

from gsai.agents.tools.deps import FileToolDeps
from gsai.display_helpers import (
    overwrite_file_description,
    with_progress_display,
)
from gsai.security import SecurityError, safe_construct_path
from gsai.utils import safe_open_w


@with_progress_display("overwrite_file", overwrite_file_description)
def overwrite_file(
    ctx: RunContext[FileToolDeps],
    relative_file_path: str,
    new_file_text: str,
) -> str:
    """
    Overwrites a file with the provided content and returns a confirmation message. Only use this when str_replace tool is not applicable.

    This function writes the complete content to the specified file relative to the repository root. It is essential to supply the full content as this operation overwrites any existing file content. Ensure that the resulting code is both idiomatic and correct.

    When using the overwrite_file tool, please specify all arguments: relative_file_path, and new_file_text. The new_file_text argument should contain the complete content of the file as a multi-line string.

    WARNING: if new_file_text PARAMETER is not provide this tool will fail. YOU MUST PROVIDE new_file_text PARAMETER

    Before using this tool:
    1. Use the view_file tool to understand the file's contents and context
    2. Directory Verification (only applicable when creating new files):
    - Use the list_files tool to verify the parent directory exists and is the correct location

    IMPORTANT: To use this command YOU MUST SPECIFY new_file_text or else it will fail. The new_file_text parameter will become the new content of the file, so be careful with
    existing files! This is a full overwrite, so you must include everything - not just sections you are modifying. Also When using the overwrite_file tool, please structure your call exactly like this:
    <EXAMPLE>
    overwrite_file(
        relative_file_path="your/path/here.py",
        new_file_text="""
    # Your complete code here including the sections you do not want to modify
    """
    )
    </EXAMPLE>

    IMPORTANT: When specifying paths always use paths relative to the repo path which is: {{repo_path}}.
    Here are some exmaples given the repo path of /data/repos/instance-2123/client-acme-test:
    - if you want to view, modify, or create `/data/repos/instance-2123/client-acme-test/Dockerfile` then use `Dockerfile` as the path
    - if you want to view, modify, or create `/data/repos/instance-2123/client-acme-test/app/main.py` then use `app/main.py` as the path
    - if you want to view, modify, or create `/data/repos/instance-2123/client-acme-test/app/components/CoolComp.tsx` then use `app/components/CoolComp.tsx` as the path

    :param relative_file_path: The relative path to the file from the repository root where the content should be written.
    :type relative_file_path: str
    :param new_file_text: A string containing the complete content to write to the file.
    :type new_file_text: str

    :returns: A confirmation message indicating that the file has been successfully written.
    :rtype: str
    """
    try:
        # Read original content for diff visualization
        full_file_path = safe_construct_path(ctx.deps.repo_path, relative_file_path)
        original_content = ""
        try:
            with open(full_file_path) as f:
                original_content = f.read()
        except FileNotFoundError:
            # File doesn't exist yet, original content is empty
            original_content = ""

        # Check approval for file write operation with diff visualization
        safe_path = ctx.deps.approval_manager.validate_file_operation(
            "overwrite_file",
            relative_file_path,
            f"Overwrite {relative_file_path}",
            original_content,
            new_file_text,
        )

        full_file_path = safe_construct_path(ctx.deps.repo_path, safe_path)

        logger.info(f"Overwriting file: {full_file_path}")

        with safe_open_w(full_file_path) as output_file:
            output_file.write(new_file_text)

        return f"File overwritten successfully: {full_file_path}"
    except SecurityError as e:
        return f"Security error: {e}"
    except Exception as e:
        return f"Error overwriting file: {e}"
