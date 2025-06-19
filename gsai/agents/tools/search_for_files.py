"""File search tool for AI Coding CLI."""

import glob
import os
from typing import Annotated

from annotated_types import MinLen
from loguru import logger
from pydantic_ai import RunContext

from gsai.agents.tools.deps import CodebaseDeps
from gsai.display_helpers import (
    search_files_description,
    with_progress_display,
)


def search_files_by_glob(
    repo_path: str, relative_pattern: str, recursive: bool = True
) -> list[str]:
    """
    Search for files using glob patterns.

    Args:
        repo_path: The repository path
        relative_pattern: The glob pattern to search for
        recursive: Whether to search recursively

    Returns:
        List of matching file paths
    """
    # Construct the full pattern
    if recursive and "**" not in relative_pattern:
        pattern = os.path.join(repo_path, "**", relative_pattern)
    else:
        pattern = os.path.join(repo_path, relative_pattern)

    # Use glob to find matching files
    matches = glob.glob(pattern, recursive=recursive)

    # Return relative paths
    return [os.path.relpath(match, repo_path) for match in matches]


@with_progress_display("search_for_files", search_files_description)
def search_for_files(
    ctx: RunContext[CodebaseDeps],
    glob_pattern: Annotated[str, MinLen(1)],
    recursive: bool = True,
) -> list[str]:
    """
    Searches for files in the repository that match a given glob pattern.

    This function uses the provided glob pattern to locate files within the repository defined in the run context. It can perform recursive searches when enabled.

    - Supports glob patterns like "**/*.js" or "src/**/*.ts"
    - Use this tool when you need to find files by name patterns

    <glob_pattern_examples>
        <pattern syntax="*.txt">
            <matches>file.txt, document.txt</matches>
            <description>Any filename ending with .txt in current directory</description>
        </pattern>

        <pattern syntax="?.txt">
            <matches>a.txt, b.txt</matches>
            <description>Single character followed by .txt</description>
        </pattern>

        <pattern syntax="[abc].txt">
            <matches>a.txt, b.txt, c.txt</matches>
            <description>One character from the set [a,b,c] followed by .txt</description>
        </pattern>

        <pattern syntax="[!abc].txt">
            <matches>d.txt, e.txt</matches>
            <description>One character NOT in the set [a,b,c] followed by .txt</description>
        </pattern>

        <pattern syntax="[0-9].txt">
            <matches>0.txt through 9.txt</matches>
            <description>Any single digit followed by .txt</description>
        </pattern>

        <pattern syntax="dir/*.txt">
            <matches>dir/file.txt, dir/document.txt</matches>
            <description>Any .txt file in the 'dir' directory only</description>
        </pattern>

        <pattern syntax="*/*.txt">
            <matches>dir1/file.txt, dir2/file.txt</matches>
            <description>Any .txt file in any immediate subdirectory</description>
        </pattern>

        <pattern syntax="**/*.txt">
            <matches>file.txt, dir/file.txt, dir/subdir/file.txt</matches>
            <description>Any .txt file in current directory or any subdirectory at any depth</description>
        </pattern>

        <pattern syntax="dir/**/*.py">
            <matches>dir/file.py, dir/subdir/file.py</matches>
            <description>Any .py file in 'dir' or any of its subdirectories</description>
        </pattern>

        <pattern syntax="**/dir/*.json">
            <matches>dir/*.json, subdir/dir/*.json</matches>
            <description>Any .json file in any directory named 'dir' at any depth</description>
        </pattern>

        <pattern syntax="**/{bin,src}/**/*.js">
            <matches>bin/file.js, src/file.js, a/bin/b/file.js</matches>
            <description>Any .js file in directories named 'bin' or 'src' at any depth</description>
        </pattern>

        <pattern syntax="**/test_*.py">
            <matches>test_file.py, dir/test_util.py</matches>
            <description>Any python file starting with 'test_' at any depth</description>
        </pattern>

        <pattern syntax="docs/**/*.{md,txt}">
            <matches>docs/file.md, docs/file.txt, docs/api/readme.md</matches>
            <description>Any .md or .txt file under the 'docs' directory at any depth</description>
        </pattern>
        </glob_pattern_examples>


    :param glob_pattern: A non-empty string representing the glob pattern to match file names.
    :type glob_pattern: str
    :param recursive: A boolean flag indicating whether the search should be performed recursively.
    :type recursive: bool
    :returns: A list of matching file paths (as strings) relative to the repository path, or an error message if the repository path is not provided.
    :rtype: list[str]
    """
    logger.info(
        f"Searching for files with pattern: {glob_pattern}, recursive: {recursive}"
    )

    return search_files_by_glob(ctx.deps.repo_path, glob_pattern, recursive)
