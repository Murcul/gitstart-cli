"""Code search tool for AI Coding CLI."""

import re
import subprocess

import tiktoken
from loguru import logger
from pydantic_ai import RunContext

from gsai.agents.tools.deps import CodebaseDeps
from gsai.display_helpers import (
    search_code_description,
    with_progress_display,
)
from gsai.security import safe_construct_path


def use_grep_ast(
    pattern: str,
    filenames: str = ".",
    case_sensitive: bool = True,
) -> str:
    """
    Advanced file search using grep_ast that provides AST context for matches.

    Args:
        pattern: Pattern to search for in files
        filenames: directory or file to search
        case_sensitive: Whether search is case-sensitive

    Returns:
        String containing the grep_ast output with AST context
    """
    # Build the grep_ast command
    cmd = ["grep-ast"]

    # Add case insensitive flag if needed
    if not case_sensitive:
        cmd.append("-i")

    cmd.append("--no-color")

    # Add the search pattern
    cmd.append(pattern)

    # Add the filenames
    cmd.append(filenames)

    # Execute the command
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )

    # Return the output
    return result.stdout


@with_progress_display("search_for_code", search_code_description)
def search_for_code(
    ctx: RunContext[CodebaseDeps],
    pattern: str,
    case_sensitive: bool,
    relative_path: str = ".",
) -> str:
    """
    Searches through the contents of files for code patterns within the files in the relative path provided  with MINIMAL TOKEN USE.
    Returns with not only the matching files but also critical code context.
    - Fast content search tool that works with any codebase size
    - Searches file contents using regular expressions
    - Can support full regex syntax (eg. "log.*Error", "function\\s+\\w+", etc.)
    - Searches in relative path, which can be a directory or a file
    - Use this tool when you need to find files containing specific patterns

    GREAT USE CASES:
    - Find all files that reference a function
    - Doing a migration? Need to update the way something is used? This is great
    - Looking for how a class is used throughout the code
    - Basically any time you want to find code.

    NOTE: If the result is too large, only file paths will be returned. Use this information to refine your search.

    :param pattern: The text or regular expression pattern to search for within files.
    :type pattern: str
    :param case_sensitive: A boolean flag indicating whether the search should consider case sensitivity.
    :type case_sensitive: bool
    :param relative_path: A relative path to a file or directory (relative to repo_path)
    :type relative_path: str
    :returns: Code context that matches your search for every file where the pattern was found, IF the result is too large, only file paths where the code is contained will be returned
    :rtype: str
    """
    logger.info(f"Searching for code - Pattern: {pattern} in Path: {relative_path}")

    # Fallback without display
    full_file_path = safe_construct_path(ctx.deps.repo_path, relative_path)
    result = use_grep_ast(
        pattern,
        full_file_path,
        case_sensitive=case_sensitive,
    )

    encoding = tiktoken.get_encoding("o200k_base")
    output_token_length = len(encoding.encode(result))

    # If the result is too large, just return the file paths that are relevant
    if output_token_length > 50000:
        lines = result.splitlines()
        re_pattern = re.compile(r"^(/.*[/\\][^/\\]+):$")
        matching_paths = []
        for line in lines:
            match = re_pattern.match(line)
            if match:
                matching_paths.append(match.group(1))
        return "\n".join(matching_paths)
    return result
