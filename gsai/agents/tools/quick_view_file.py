from loguru import logger
from pydantic_ai import RunContext

from gsai.agents.tools.deps import CodebaseDeps
from gsai.display_helpers import quick_view_description, with_progress_display
from gsai.repo_map import RepoMap
from gsai.security import safe_construct_path
from gsai.utils import get_files_excluding_gitignore, safe_str_for_log


@with_progress_display("quick_view_file", quick_view_description)
def quick_view_file(
    ctx: RunContext[CodebaseDeps], relative_path: str, opened_files: list[str] = []
) -> str:
    """
    Extract essential context (key definitions, structures, and interfaces) from files
    without analyzing entire file contents with MINIMAL TOKEN USE.

    This will only work for code files. It will not work for templates, text formats, etc. It uses an AST to show these structures.
    If you don't find anything with this tool you can try the normal view_file tool to see the contents of the file.

    This function creates a concise, structured representation of code by identifying key
    elements such as function definitions, class declarations, and important interfaces.
    It intelligently skips previously opened files to avoid redundancy.

    :param relative_path: A relative path to a file or directory (relative to repo_path). If a directory is provided,
                          all relevant files within it will be processed
    :type relative_path: str
    :param opened_files: List of file paths that have been previously processed
                        and should be excluded from the current analysis, defaults to []
    :type opened_files: list[str], optional
    :return: A structured representation of the essential code context from the analyzed files,
             including key definitions, interfaces, and relationships between components
    :rtype: str
    :note: This function is more efficient than analyzing entire file contents and should be
           preferred when only structural code information is needed.
    """
    full_file_path = safe_construct_path(ctx.deps.repo_path, relative_path)
    logger.info(
        safe_str_for_log(
            f"Extracting code context for repo '{ctx.deps.repo_path}' in '{full_file_path}' excluding {opened_files}"
        )
    )
    other_fnames = get_files_excluding_gitignore(ctx.deps.repo_path, full_file_path)
    rm = RepoMap(root=ctx.deps.repo_path, verbose=True)
    repo_map = rm.get_repo_map(opened_files, other_fnames)
    return repo_map
