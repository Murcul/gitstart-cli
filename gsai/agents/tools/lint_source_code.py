from loguru import logger
from pydantic_ai import RunContext

from gsai.agents.tools.deps import CodebaseDeps
from gsai.display_helpers import lint_description, with_progress_display
from gsai.linter import format_lint_result, lint_file
from gsai.security import safe_construct_path
from gsai.utils import safe_str_for_log


@with_progress_display("lint_source_code", lint_description)
def lint_source_code(
    ctx: RunContext[CodebaseDeps],
    relative_file_path: str,
) -> str:
    """
    Lints source code for syntax errors using Tree-Sitter.

    This function checks the provided file for syntax errors using the Tree-Sitter parsing library.
    It can determine the language from the file path.

    Args:
        ctx: The run context containing dependencies.
        relative_file_path: The relative path to the file within the repository.

    Returns:
        A formatted string containing lint results, including any syntax errors found.

    Usage Example:
        report = lint_source_code(ctx, "src/main.py")
    """
    logger.info(safe_str_for_log(f"Linting code with file_path={relative_file_path}"))

    # If file_path is provided but doesn't include the repo path, add it
    full_file_path = safe_construct_path(ctx.deps.repo_path, relative_file_path)

    # Perform linting
    result = lint_file(full_file_path)
    formatted_result = format_lint_result(result)
    # Format and return results
    return formatted_result
