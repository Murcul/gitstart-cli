"""save_to_memory tool for GSAI.md editing."""

from loguru import logger
from pydantic_ai import RunContext

from gsai.agents.tools.deps import FileToolDeps
from gsai.agents.tools.str_replace import str_replace
from gsai.security import safe_construct_path


def save_to_memory(
    ctx: RunContext[FileToolDeps],
    old_str: str,
    new_str: str,
) -> str:
    """
    <summary>Stores and retrieves project-specific knowledge in the GSAI.md file using precise string replacement.

    This tool is the primary mechanism for maintaining codebase preferences, user preferences, important
    codebase commands, style patterns, code conventions, architecture decisions, and recurring workflows
    that persist between conversations. It operates exactly like str_replace but is restricted to only
    writing to GSAI.md for security and organization purposes.

    Primary use cases:
    - Store codebase preferences (testing frameworks, build tools, deployment methods)
    - Document user/team preferences (coding styles, naming conventions, patterns to avoid)
    - Save important codebase commands (build, test, deploy, development workflows)
    - Record style patterns and code conventions discovered or established
    - Document architecture decisions and design patterns in use
    - Maintain recurring workflows and development processes

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

    :param old_str: The exact string to be replaced.
    :type old_str: str
    :param new_str: The string that will replace the old string.
    :type new_str: str

    :returns: A confirmation message describing the change that was made.
    :rtype: str
    """
    # Fixed file path - only allows writing to GSAI.md in repository root
    target_file_path = "./GSAI.md"
    full_file_path = safe_construct_path(ctx.deps.repo_path, target_file_path)
    logger.info(full_file_path)
    logger.info(old_str)
    logger.info(new_str)
    return str_replace(ctx, target_file_path, old_str, new_str)
