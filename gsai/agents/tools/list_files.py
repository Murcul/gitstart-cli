"""File listing tool for AI Coding CLI."""

import subprocess

from loguru import logger
from pydantic_ai import RunContext

from gsai.agents.tools.deps import CodebaseDeps
from gsai.security import safe_construct_path


def use_ls(repo_path: str, relative_file_path: str, recursive: bool) -> str:
    """
    Use the ls command to list files and directories.

    Args:
        repo_path: The repository path
        relative_file_path: The relative file path to list
        recursive: Whether to list recursively

    Returns:
        The ls command output
    """
    full_path = safe_construct_path(repo_path, relative_file_path)

    if recursive:
        cmd = ["ls", "-la", "-R", full_path]
    else:
        cmd = ["ls", "-la", full_path]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error listing files: {e.stderr}"


def list_files(
    ctx: RunContext[CodebaseDeps], relative_file_path: str, recursive: bool
) -> str:
    """
    Lists files and directories for a given relative path within the repository.

    This function constructs an absolute path based on the repository path from the run context, then executes the 'ls' command to retrieve a directory listing. It supports recursive listing when specified.

    IMPORTANT: When specifying paths always use paths relative to the repo path which is: {{repo_path}}.
    Here are some exmaples given the repo path of /data/repos/instance-2123/client-acme-test:
    - if you want to view, modify, or create `/data/repos/instance-2123/client-acme-test/Dockerfile` then use `Dockerfile` as the path
    - if you want to view, modify, or create `/data/repos/instance-2123/client-acme-test/app/main.py` then use `app/main.py` as the path
    - if you want to view, modify, or create `/data/repos/instance-2123/client-acme-test/app/components/CoolComp.tsx` then use `app/components/CoolComp.tsx` as the path

    :param relative_file_path: The relative file path from the repository root where files and directories should be listed.
    :type relative_file_path: str
    :param recursive: A boolean flag indicating whether to list files and directories recursively.
    :type recursive: bool
    :returns: A string containing the directory listing or an error message if the path is invalid or does not exist.
    :rtype: str
    """
    logger.info(f"Listing files in {relative_file_path}, recursive: {recursive}")

    return use_ls(ctx.deps.repo_path, relative_file_path, recursive)
