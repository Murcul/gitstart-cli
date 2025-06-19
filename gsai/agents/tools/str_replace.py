"""String replacement tool for AI Coding CLI."""

from loguru import logger
from pydantic_ai import ModelRetry, RunContext

from gsai.agents.tools.deps import FileToolDeps
from gsai.display_helpers import (
    str_replace_description,
    with_progress_display,
)
from gsai.security import SecurityError, safe_construct_path
from gsai.utils import safe_open_w


def write_file(file_path: str, file_content: str) -> None:
    """
    Writes content to a file at the specified path in the repository.

    Args:
        file_path: The absolute path to the file.
        file_content: The content to write to the file.
    """
    with safe_open_w(file_path) as output_file:
        output_file.write(file_content)


def replace_in_file(file_path: str, pattern: str, new_str: str) -> None:
    """
    Replaces text in a file matching a regex pattern with new text.

    Args:
        file_path: The absolute path to the file.
        pattern: The regex pattern to match for replacement.
        new_str: The string to replace matched patterns with.
    """
    with open(file_path, "r+") as output_file:
        data = output_file.read()

        # Count matches
        count = data.count(pattern)
        if count > 1:
            raise ValueError(
                f"Multiple matches ({count}) found for pattern. Only one match is allowed."
            )
        elif count == 0:
            raise ValueError("Could not find pattern.")

        # Replace the first occurrence
        new_file_text = data.replace(pattern, new_str, 1)

        output_file.seek(0)
        output_file.write(new_file_text)
        output_file.truncate()


@with_progress_display("str_replace", str_replace_description)
def str_replace(
    ctx: RunContext[FileToolDeps],
    relative_file_path: str,
    old_str: str,
    new_str: str,
) -> str:
    """
    This is a tool for editing files and inserting into a file. For very large edits or creating a file, use the overwrite_file tool to overwrite files.

    This tool should be used even when you want to insert into a file, just provide the context as the old_str and replace with new_str that does not modify the old context,.

    IMPORTANT: To use the str_replace command, you must specify both `old_str` and `new_str` - the `old_str` needs to exactly match one
    unique section of the original file, including any whitespace. Make sure to include enough context that the match is not
    ambiguous. The entire original string will be replaced with `new_str`. So to make sure that you don't accidentally modify previously existing code, include it when relevant in your new str.

    Before using this tool:
        1. Use the View tool to understand the file's contents and context
        2. Verify the directory path is correct (only applicable when creating new files):
            - Use the LS tool to verify the parent directory exists and is the correct location
    To make a file edit, provide the following:
        1. relative_file_path: The relative path to the file to modify
        2. old_str: The text to replace (must be unique within the file, and must match the file contents exactly, including all whitespace and indentation)
        3. new_str: The edited text to replace the old_string

    The tool will replace ONE occurrence of old_string with new_string in the specified file. If there is more than ONE occurrence of old_string, it will fail.
    CRITICAL REQUIREMENTS FOR USING THIS TOOL:
        1. UNIQUENESS: The old_string MUST uniquely identify the specific instance you want to change. This means:
            - Include AT LEAST 3-5 lines of context BEFORE the change point
            - Include AT LEAST 3-5 lines of context AFTER the change point
            - Include all whitespace, indentation, and surrounding code exactly as it appears in the file
        2. SINGLE INSTANCE: This tool can only change ONE instance at a time. If you need to change multiple instances:
            - Make separate calls to this tool for each instance
            - Each call must uniquely identify its specific instance using extensive context
        3. VERIFICATION: Before using this tool:
            - Check how many instances of the target text exist in the file
            - If multiple instances exist, gather enough context to uniquely identify each one
            - Plan separate tool calls for each instance
    WARNING: If you do not follow these requirements:
        - The tool will fail if old_string matches multiple locations
        - The tool will fail if old_string doesn't match exactly (including whitespace)
        - You may change the wrong instance if you don't include enough context
    When making edits:
        - Ensure the edit results in idiomatic, correct code
        - Do not leave the code in a broken state

    If you want to create a new file, use:
        - A new file path, including dir name if needed
        - An empty old_string
        - The new file's contents as new_string

    Remember: when making multiple file edits in a row to the same file, you should prefer to send all edits in a single message with multiple calls to this tool, rather than multiple messages with a single call each.

    IMPORTANT: When specifying paths always use paths relative to the repo path which is: {{repo_path}}.
    Here are some exmaples given the repo path of /data/repos/instance-2123/client-acme-test:
    - if you want to view, modify, or create `/data/repos/instance-2123/client-acme-test/Dockerfile` then use `Dockerfile` as the path
    - if you want to view, modify, or create `/data/repos/instance-2123/client-acme-test/app/main.py` then use `app/main.py` as the path
    - if you want to view, modify, or create `/data/repos/instance-2123/client-acme-test/app/components/CoolComp.tsx` then use `app/components/CoolComp.tsx` as the path

    :param relative_file_path: The relative path to the file within the repository.
    :type relative_file_path: str
    :param old_str: The exact string to be replaced.
    :type old_str: str
    :param new_str: The string that will replace the old string.
    :type new_str: str

    :returns: A confirmation message describing the change that was made.
    :rtype: str
    """
    # Check approval for file write operation
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

        # Generate new content for diff visualization
        if old_str == "":
            new_content = new_str
        else:
            new_content = original_content.replace(old_str, new_str, 1)

        safe_path = ctx.deps.approval_manager.validate_file_operation(
            "str_replace",
            relative_file_path,
            f"Replace text in {relative_file_path}",
            original_content,
            new_content,
        )

        full_file_path = safe_construct_path(ctx.deps.repo_path, safe_path)

        if old_str == "":
            logger.info(f"Writing to {full_file_path}")
            write_file(full_file_path, new_str)
        else:
            logger.info(f"Making a replacement in {full_file_path}")
            try:
                replace_in_file(full_file_path, old_str, new_str)
            except FileNotFoundError as error:
                raise ModelRetry(f"{error}, relative_file_path: {safe_path}")
            except ValueError as error:
                raise ModelRetry(f"{error}")

        return f"str_replace edit successful in {full_file_path}"
    except SecurityError as e:
        return f"Security error: {e}"
    except Exception as e:
        return f"Error replacing text: {e}"
