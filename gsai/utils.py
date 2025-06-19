import os
from io import TextIOWrapper

import pathspec
from loguru import logger


def safe_str_for_log(s: str) -> str:
    """Escape braces in strings for safe logging."""
    return s.replace("{", "{{").replace("}", "}}")


def safe_open_w(path: str) -> TextIOWrapper:
    """Open "path" for writing, creating any parent directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, "w")


def get_files_excluding_gitignore(repo_path: str, abs_path: str) -> list[str]:
    """
    Get all file names in a directory, excluding patterns in .gitignore and the .git directory.
    Uses pathspec library for accurate .gitignore pattern matching.

    Args:
        repo_path (str): absolute path to the repo that should contain the gitignore
        abs_path (str): Absolute path to file or directory

    Returns:
        list: List of file paths that don't match .gitignore patterns and aren't in .git
    """
    from gsai.security import safe_construct_path

    # Check if the directory exists
    if not os.path.isdir(repo_path):
        raise ValueError(f"The directory '{repo_path}' does not exist")

    # Create a PathSpec instance from gitignore if it exists
    spec = None
    gitignore_path = os.path.join(repo_path, ".gitignore")
    if os.path.isfile(gitignore_path):
        with open(gitignore_path) as f:
            # Create the pathspec object with gitignore patterns
            spec = pathspec.PathSpec.from_lines("gitwildmatch", f)

    # Add .git directory to always be ignored even if not in .gitignore
    if spec:
        # Add an explicit pattern for the .git directory
        spec += pathspec.PathSpec.from_lines("gitwildmatch", [".git/"])
    else:
        # If no .gitignore exists, create a spec just for .git
        spec = pathspec.PathSpec.from_lines("gitwildmatch", [".git/"])

    results: list[str] = []
    if os.path.isdir(abs_path):
        results = list(spec.match_tree(abs_path, negate=True))
    else:
        if not spec.match_file(abs_path):
            results = [abs_path]

    results = [safe_construct_path(abs_path, result) for result in results]
    return results


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
