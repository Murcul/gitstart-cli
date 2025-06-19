"""
Linter module for syntax checking using Tree-Sitter.

This module provides functionality to parse code and detect syntax errors
using the Tree-Sitter parsing library. It supports multiple languages
and provides detailed error reporting.
"""

import os
from dataclasses import dataclass

from loguru import logger
from tree_sitter import Node, Parser, Tree
from tree_sitter_language_pack import SupportedLanguage, get_parser

# Dictionary to store language parsers
LANGUAGE_PARSERS: dict[str, Parser] = {}

# Dictionary mapping file extensions to language identifiers
EXTENSION_TO_LANGUAGE: dict[str, SupportedLanguage] = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".jsx": "javascript",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".go": "go",
    ".rb": "ruby",
    ".rs": "rust",
    ".php": "php",
}


@dataclass
class LintError:
    """Class representing a syntax error found during linting."""

    message: str
    line: int
    column: int
    severity: str = "error"
    code: str | None = None
    source: str | None = None


@dataclass
class LintResult:
    """Class representing the result of a linting operation."""

    success: bool
    errors: list[LintError]
    file_path: str | None = None
    language: str | None = None


def get_language_from_file_extension(file_path: str) -> SupportedLanguage | None:
    """
    Determine the programming language based on file extension.

    Args:
        file_path: Path to the file

    Returns:
        Language identifier or None if not recognized
    """
    ext = os.path.splitext(file_path)[1].lower()
    return EXTENSION_TO_LANGUAGE.get(ext)


def get_language_from_content(content: str) -> str | None:
    """
    Attempt to determine the programming language from content.
    This is a fallback when file extension is not available.

    Args:
        content: The code content to analyze

    Returns:
        Language identifier or None if not determined
    """
    # Simple heuristics to guess language
    if (
        "def " in content
        and ":" in content
        and ("import " in content or "from " in content)
    ):
        return "python"

    # Add more heuristics for other languages as needed

    return None


def initialize_parser(language_name: SupportedLanguage) -> Parser | None:
    """
    Initialize a Tree-Sitter parser for the specified language.

    Args:
        language_name: Name of the language to initialize

    Returns:
        Initialized parser or None if initialization failed
    """
    if language_name in LANGUAGE_PARSERS:
        return LANGUAGE_PARSERS[language_name]

    try:
        # Import the language library
        parser = get_parser(language_name)
        LANGUAGE_PARSERS[language_name] = parser
        logger.info(f"Successfully initialized parser for {language_name}")
        return parser
    except Exception as e:
        logger.error(f"Failed to initialize parser for {language_name}: {e}")
        return None


def find_syntax_errors(tree: Tree, source_code: str) -> list[LintError]:
    """
    Find syntax errors in the parse tree.

    Args:
        tree: Tree-Sitter parse tree
        source_code: Original source code

    Returns:
        List of LintError objects
    """
    errors = []

    # Check for ERROR nodes in the tree
    root_node = tree.root_node

    def traverse_node(node: Node) -> None:
        if node.type == "ERROR":
            # Get line and column information
            start_point = node.start_point
            line, column = start_point

            # Get context around the error
            lines = source_code.splitlines()
            context = lines[line] if line < len(lines) else ""

            # Create error message
            message = f"Syntax error at line {line + 1}, column {column + 1}"

            # Add error to the list
            errors.append(
                LintError(
                    message=message,
                    line=line + 1,  # 1-based line numbering for user-facing messages
                    column=column + 1,  # 1-based column numbering
                    code=context,
                    source="tree-sitter",
                )
            )

        # Recursively check children
        for child in node.children:
            traverse_node(child)

    traverse_node(root_node)

    # If no explicit errors but the tree doesn't cover the entire input,
    # there's likely a syntax error
    if not errors and root_node.end_byte < len(source_code.encode()):
        # Find the line and column of the end of parsed content
        parsed_text = source_code[: root_node.end_byte]
        if isinstance(parsed_text, bytes):
            parsed_text = parsed_text.decode("utf-8")

        lines = parsed_text.splitlines()
        line = len(lines)

        # Get context around where parsing stopped
        all_lines = source_code.splitlines()
        context = all_lines[line - 1] if line - 1 < len(all_lines) else ""

        errors.append(
            LintError(
                message=f"Syntax error detected near line {line}",
                line=line,
                column=1,  # We don't know exact column
                code=context,
                source="tree-sitter",
            )
        )

    return errors


def lint_code(code: str, file_path: str) -> LintResult:
    """
    Lint code for syntax errors using Tree-Sitter.

    Args:
        code: Source code to lint
        file_path: Path to the file (optional, used to determine language if not specified)

    Returns:
        LintResult object containing success status and any errors
    """
    # Determine language if not provided
    language = get_language_from_file_extension(file_path)

    if not language:
        return LintResult(
            success=False,
            errors=[
                LintError(
                    message="Could not determine language for linting",
                    line=0,
                    column=0,
                    severity="error",
                )
            ],
            file_path=file_path,
            language=None,
        )

    # Initialize parser for the language
    parser = initialize_parser(language)
    if not parser:
        return LintResult(
            success=False,
            errors=[
                LintError(
                    message=f"Parser for language '{language}' is not available",
                    line=0,
                    column=0,
                    severity="error",
                )
            ],
            file_path=file_path,
            language=language,
        )

    # Parse the code
    try:
        tree = parser.parse(bytes(code, "utf8"))

        # Find syntax errors
        errors = find_syntax_errors(tree, code)
        return LintResult(
            success=len(errors) == 0,
            errors=errors,
            file_path=file_path,
            language=language,
        )
    except Exception as e:
        logger.error(f"Error during parsing: {e}")
        return LintResult(
            success=False,
            errors=[
                LintError(
                    message=f"Error during parsing: {str(e)}",
                    line=0,
                    column=0,
                    severity="error",
                )
            ],
            file_path=file_path,
            language=language,
        )


def lint_file(file_path: str) -> LintResult:
    """
    Lint a file for syntax errors.

    Args:
        file_path: Path to the file to lint

    Returns:
        LintResult object containing success status and any errors
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            code = f.read()

        return lint_code(code, file_path=file_path)
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return LintResult(
            success=False,
            errors=[
                LintError(
                    message=f"Error reading file: {str(e)}",
                    line=0,
                    column=0,
                    severity="error",
                )
            ],
            file_path=file_path,
            language=None,
        )


def format_lint_result(result: LintResult) -> str:
    """
    Format a LintResult into a human-readable string.

    Args:
        result: LintResult to format

    Returns:
        Formatted string representation of the lint result
    """
    if result.success:
        logger.info(f"No syntax errors found in {result.file_path or 'code'}")
        return f"No syntax errors found in {result.file_path or 'code'}"

    logger.info(f"Syntax errors were found in {result.file_path or 'code'}")
    output = []
    if result.file_path:
        output.append(f"Syntax errors in {result.file_path}:")
    else:
        output.append("Syntax errors found:")

    for error in result.errors:
        error_line = f"Line {error.line}, Column {error.column}: {error.message}"
        output.append(error_line)

        if error.code:
            output.append(f"  {error.code}")
            # Add pointer to the column position
            if error.column > 0:
                output.append(f"  {' ' * (error.column - 1)}^")

    return "\n".join(output)


def install_language(language_name: str) -> bool:
    """
    Install a Tree-Sitter language parser.

    Args:
        language_name: Name of the language to install

    Returns:
        True if installation was successful, False otherwise
    """
    try:
        # Try to install using tree_sitter_languages
        try:
            import importlib

            importlib.import_module(f"tree_sitter_{language_name}")
            logger.info(f"Language {language_name} is already installed")
            return True
        except ImportError:
            # Try to install using pip
            import subprocess

            logger.info(f"Installing tree-sitter-{language_name}...")
            result = subprocess.run(
                ["pip", "install", f"tree-sitter-{language_name}"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                logger.info(f"Successfully installed tree-sitter-{language_name}")
                return True
            else:
                logger.error(
                    f"Failed to install tree-sitter-{language_name}: {result.stderr}"
                )
                return False
    except Exception as e:
        logger.error(f"Error installing language {language_name}: {e}")
        return False


def get_supported_languages() -> list[str]:
    """
    Get a list of supported languages.

    Returns:
        List of supported language identifiers
    """
    return list(EXTENSION_TO_LANGUAGE.values())
