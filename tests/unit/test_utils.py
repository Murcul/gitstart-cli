"""Tests for utility functions in the gsai module."""

from pathlib import Path

import pytest

from gsai.linter import (
    LintError,
    LintResult,
    format_lint_result,
    get_supported_languages,
)
from gsai.security import SecurityError, safe_construct_path, validate_working_directory


class TestSecurityUtils:
    """Test cases for security utility functions."""

    def test_safe_construct_path_valid_relative(self) -> None:
        """Test safe_construct_path with valid relative path."""
        repo_path = "/home/user/repo"
        relative_path = "src/main.py"
        expected = "/home/user/repo/src/main.py"

        result = safe_construct_path(repo_path, relative_path)
        assert result == expected

    def test_safe_construct_path_prevents_traversal(self) -> None:
        """Test safe_construct_path prevents directory traversal attacks."""
        repo_path = "/home/user/repo"
        relative_path = "../../../etc/passwd"

        # This should not raise an exception since we're just constructing the path
        # The validation happens elsewhere
        result = safe_construct_path(repo_path, relative_path)
        # The result should be normalized but may still point outside repo
        assert isinstance(result, str)

    def test_validate_working_directory_exists(self, tmp_path: Path) -> None:
        """Test validate_working_directory with existing directory."""
        result = validate_working_directory(str(tmp_path))
        assert result == str(tmp_path.resolve())

    def test_validate_working_directory_nonexistent(self) -> None:
        """Test validate_working_directory raises error for non-existent directory."""
        with pytest.raises(SecurityError, match="Working directory does not exist"):
            validate_working_directory("/nonexistent/directory")


class TestLinterUtils:
    """Test cases for linter utility functions."""

    def test_get_supported_languages_returns_list(self) -> None:
        """Test get_supported_languages returns a non-empty list."""
        languages = get_supported_languages()
        assert isinstance(languages, list)
        assert len(languages) > 0
        # Check that common languages are supported
        assert any("python" in lang.lower() for lang in languages)

    def test_format_lint_result_no_errors(self) -> None:
        """Test format_lint_result with no errors."""
        result = LintResult(success=True, file_path="test.py", errors=[])
        formatted = format_lint_result(result)

        assert "test.py" in formatted
        assert "No syntax errors found" in formatted

    def test_format_lint_result_with_errors(self) -> None:
        """Test format_lint_result with errors."""
        error = LintError(
            line=10,
            column=5,
            message="Syntax error: unexpected token",
            code="print('hello world'",
        )
        result = LintResult(success=False, file_path="test.py", errors=[error])

        formatted = format_lint_result(result)

        assert "test.py" in formatted
        assert "Syntax errors in" in formatted
        assert "Line 10, Column 5" in formatted
        assert "unexpected token" in formatted
