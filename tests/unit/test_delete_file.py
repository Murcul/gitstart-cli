"""Tests for the delete_file tool functionality."""

from pathlib import Path
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest
from pydantic_ai import RunContext

from gsai.agents.tools.delete_file import delete_file
from gsai.agents.tools.deps import FileToolDeps
from gsai.security import SecurityError


class TestDeleteFile:
    """Test cases for delete_file tool functionality."""

    @pytest.fixture
    def mock_ctx(self) -> RunContext[FileToolDeps]:
        """Create a mock RunContext with FileToolDeps."""
        ctx = MagicMock(spec=RunContext)
        ctx.deps = MagicMock(spec=FileToolDeps)
        ctx.deps.repo_path = "/test/repo"
        ctx.deps.approval_manager = MagicMock()
        return ctx

    def _mock(self, obj: Any) -> MagicMock:
        """Helper to cast objects to MagicMock for mypy."""
        return cast(MagicMock, obj)

    @patch("gsai.agents.tools.delete_file.safe_construct_path")
    @patch("gsai.agents.tools.delete_file.os.path.exists")
    @patch("gsai.agents.tools.delete_file.os.path.isfile")
    @patch("gsai.agents.tools.delete_file.os.remove")
    def test_delete_file_success(
        self,
        mock_remove: MagicMock,
        mock_isfile: MagicMock,
        mock_exists: MagicMock,
        mock_safe_construct_path: MagicMock,
        mock_ctx: RunContext[FileToolDeps],
    ) -> None:
        """Test successful file deletion."""
        # Setup mocks
        self._mock(
            mock_ctx.deps.approval_manager.validate_file_operation
        ).return_value = "test.txt"
        mock_safe_construct_path.return_value = "/test/repo/test.txt"
        mock_exists.return_value = True
        mock_isfile.return_value = True

        # Execute
        result = delete_file(mock_ctx, "test.txt")

        # Verify
        assert result == "File deleted successfully: test.txt"
        self._mock(
            mock_ctx.deps.approval_manager.validate_file_operation
        ).assert_called_once_with("delete_file", "test.txt", "Delete test.txt")
        mock_safe_construct_path.assert_called_once_with("/test/repo", "test.txt")
        mock_exists.assert_called_once_with("/test/repo/test.txt")
        mock_isfile.assert_called_once_with("/test/repo/test.txt")
        mock_remove.assert_called_once_with("/test/repo/test.txt")

    @patch("gsai.agents.tools.delete_file.safe_construct_path")
    @patch("gsai.agents.tools.delete_file.os.path.exists")
    def test_delete_file_not_found(
        self,
        mock_exists: MagicMock,
        mock_safe_construct_path: MagicMock,
        mock_ctx: RunContext[FileToolDeps],
    ) -> None:
        """Test deletion of non-existent file."""
        # Setup mocks
        self._mock(
            mock_ctx.deps.approval_manager.validate_file_operation
        ).return_value = "nonexistent.txt"
        mock_safe_construct_path.return_value = "/test/repo/nonexistent.txt"
        mock_exists.return_value = False

        # Execute
        result = delete_file(mock_ctx, "nonexistent.txt")

        # Verify
        assert result == "Error: File does not exist: nonexistent.txt"

    @patch("gsai.agents.tools.delete_file.safe_construct_path")
    @patch("gsai.agents.tools.delete_file.os.path.exists")
    @patch("gsai.agents.tools.delete_file.os.path.isfile")
    def test_delete_file_is_directory(
        self,
        mock_isfile: MagicMock,
        mock_exists: MagicMock,
        mock_safe_construct_path: MagicMock,
        mock_ctx: RunContext[FileToolDeps],
    ) -> None:
        """Test deletion attempt on directory."""
        # Setup mocks
        self._mock(
            mock_ctx.deps.approval_manager.validate_file_operation
        ).return_value = "test_dir"
        mock_safe_construct_path.return_value = "/test/repo/test_dir"
        mock_exists.return_value = True
        mock_isfile.return_value = False

        # Execute
        result = delete_file(mock_ctx, "test_dir")

        # Verify
        assert (
            result == "Error: Path is not a file (directories not supported): test_dir"
        )

    def test_delete_file_security_error(
        self, mock_ctx: RunContext[FileToolDeps]
    ) -> None:
        """Test handling of security errors from approval manager."""
        # Setup mocks
        self._mock(
            mock_ctx.deps.approval_manager.validate_file_operation
        ).side_effect = SecurityError("Access denied")

        # Execute
        result = delete_file(mock_ctx, "restricted.txt")

        # Verify
        assert result == "Security error: Access denied"

    @patch("gsai.agents.tools.delete_file.safe_construct_path")
    @patch("gsai.agents.tools.delete_file.os.path.exists")
    @patch("gsai.agents.tools.delete_file.os.path.isfile")
    @patch("gsai.agents.tools.delete_file.os.remove")
    def test_delete_file_os_error(
        self,
        mock_remove: MagicMock,
        mock_isfile: MagicMock,
        mock_exists: MagicMock,
        mock_safe_construct_path: MagicMock,
        mock_ctx: RunContext[FileToolDeps],
    ) -> None:
        """Test handling of OS errors during file deletion."""
        # Setup mocks
        self._mock(
            mock_ctx.deps.approval_manager.validate_file_operation
        ).return_value = "test.txt"
        mock_safe_construct_path.return_value = "/test/repo/test.txt"
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_remove.side_effect = OSError("Permission denied")

        # Execute
        result = delete_file(mock_ctx, "test.txt")

        # Verify
        assert result == "Error deleting file: Permission denied"

    @patch("gsai.agents.tools.delete_file.safe_construct_path")
    @patch("gsai.agents.tools.delete_file.os.path.exists")
    @patch("gsai.agents.tools.delete_file.os.path.isfile")
    @patch("gsai.agents.tools.delete_file.os.remove")
    def test_delete_file_with_subdirectory_path(
        self,
        mock_remove: MagicMock,
        mock_isfile: MagicMock,
        mock_exists: MagicMock,
        mock_safe_construct_path: MagicMock,
        mock_ctx: RunContext[FileToolDeps],
    ) -> None:
        """Test deletion of file in subdirectory."""
        # Setup mocks
        self._mock(
            mock_ctx.deps.approval_manager.validate_file_operation
        ).return_value = "src/main.py"
        mock_safe_construct_path.return_value = "/test/repo/src/main.py"
        mock_exists.return_value = True
        mock_isfile.return_value = True

        # Execute
        result = delete_file(mock_ctx, "src/main.py")

        # Verify
        assert result == "File deleted successfully: src/main.py"
        self._mock(
            mock_ctx.deps.approval_manager.validate_file_operation
        ).assert_called_once_with("delete_file", "src/main.py", "Delete src/main.py")
        mock_safe_construct_path.assert_called_once_with("/test/repo", "src/main.py")
        mock_remove.assert_called_once_with("/test/repo/src/main.py")

    def test_delete_file_approval_manager_validation(
        self, mock_ctx: RunContext[FileToolDeps]
    ) -> None:
        """Test that approval manager is called with correct parameters."""
        # Setup mocks
        self._mock(
            mock_ctx.deps.approval_manager.validate_file_operation
        ).side_effect = SecurityError("Rejected")

        # Execute
        delete_file(mock_ctx, "important.txt")

        # Verify approval manager was called correctly
        self._mock(
            mock_ctx.deps.approval_manager.validate_file_operation
        ).assert_called_once_with(
            "delete_file", "important.txt", "Delete important.txt"
        )

    @patch("gsai.agents.tools.delete_file.safe_construct_path")
    @patch("gsai.agents.tools.delete_file.os.path.exists")
    @patch("gsai.agents.tools.delete_file.os.path.isfile")
    @patch("gsai.agents.tools.delete_file.os.remove")
    def test_delete_file_path_construction(
        self,
        mock_remove: MagicMock,
        mock_isfile: MagicMock,
        mock_exists: MagicMock,
        mock_safe_construct_path: MagicMock,
        mock_ctx: RunContext[FileToolDeps],
    ) -> None:
        """Test that path construction uses safe_construct_path correctly."""
        # Setup mocks
        self._mock(
            mock_ctx.deps.approval_manager.validate_file_operation
        ).return_value = "validated/path.txt"
        mock_safe_construct_path.return_value = "/test/repo/validated/path.txt"
        mock_exists.return_value = True
        mock_isfile.return_value = True

        # Execute
        delete_file(mock_ctx, "original/path.txt")

        # Verify safe_construct_path was called with validated path
        mock_safe_construct_path.assert_called_once_with(
            "/test/repo", "validated/path.txt"
        )

    @patch("gsai.agents.tools.delete_file.safe_construct_path")
    @patch("gsai.agents.tools.delete_file.os.path.exists")
    @patch("gsai.agents.tools.delete_file.os.path.isfile")
    @patch("gsai.agents.tools.delete_file.os.remove")
    def test_delete_file_filenotfound_exception(
        self,
        mock_remove: MagicMock,
        mock_isfile: MagicMock,
        mock_exists: MagicMock,
        mock_safe_construct_path: MagicMock,
        mock_ctx: RunContext[FileToolDeps],
    ) -> None:
        """Test handling of FileNotFoundError exception during deletion."""
        # Setup mocks
        self._mock(
            mock_ctx.deps.approval_manager.validate_file_operation
        ).return_value = "test.txt"
        mock_safe_construct_path.return_value = "/test/repo/test.txt"
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_remove.side_effect = FileNotFoundError()

        # Execute
        result = delete_file(mock_ctx, "test.txt")

        # Verify
        assert result == "Error: File not found: test.txt"

    @patch("gsai.agents.tools.delete_file.safe_construct_path")
    @patch("gsai.agents.tools.delete_file.os.path.exists")
    @patch("gsai.agents.tools.delete_file.os.path.isfile")
    @patch("gsai.agents.tools.delete_file.os.remove")
    def test_delete_file_isdirectory_exception(
        self,
        mock_remove: MagicMock,
        mock_isfile: MagicMock,
        mock_exists: MagicMock,
        mock_safe_construct_path: MagicMock,
        mock_ctx: RunContext[FileToolDeps],
    ) -> None:
        """Test handling of IsADirectoryError exception during deletion."""
        # Setup mocks
        self._mock(
            mock_ctx.deps.approval_manager.validate_file_operation
        ).return_value = "test_dir"
        mock_safe_construct_path.return_value = "/test/repo/test_dir"
        mock_exists.return_value = True
        mock_isfile.return_value = True  # This passes the initial check
        mock_remove.side_effect = IsADirectoryError()

        # Execute
        result = delete_file(mock_ctx, "test_dir")

        # Verify
        assert result == "Error: Path is a directory, not a file: test_dir"


class TestDeleteFileIntegration:
    """Integration tests for delete_file tool with real file operations."""

    def test_delete_file_with_real_temp_file(self, temp_dir: Path) -> None:
        """Test delete_file with a real temporary file."""
        # Create a real temporary file
        test_file = temp_dir / "test_file.txt"
        test_file.write_text("test content")
        assert test_file.exists()

        # Create mock context
        ctx = MagicMock(spec=RunContext)
        ctx.deps = MagicMock(spec=FileToolDeps)
        ctx.deps.repo_path = str(temp_dir)
        ctx.deps.approval_manager = MagicMock()

        # Setup approval manager to return the relative path
        cast(
            MagicMock, ctx.deps.approval_manager.validate_file_operation
        ).return_value = "test_file.txt"

        # Execute delete_file
        with patch(
            "gsai.agents.tools.delete_file.safe_construct_path"
        ) as mock_safe_path:
            mock_safe_path.return_value = str(test_file)
            result = delete_file(ctx, "test_file.txt")

        # Verify file was deleted
        assert not test_file.exists()
        assert result == "File deleted successfully: test_file.txt"

    def test_delete_file_with_real_directory(self, temp_dir: Path) -> None:
        """Test delete_file behavior with a real directory."""
        # Create a real directory
        test_dir = temp_dir / "test_directory"
        test_dir.mkdir()
        assert test_dir.exists()
        assert test_dir.is_dir()

        # Create mock context
        ctx = MagicMock(spec=RunContext)
        ctx.deps = MagicMock(spec=FileToolDeps)
        ctx.deps.repo_path = str(temp_dir)
        ctx.deps.approval_manager = MagicMock()

        # Setup approval manager to return the relative path
        cast(
            MagicMock, ctx.deps.approval_manager.validate_file_operation
        ).return_value = "test_directory"

        # Execute delete_file
        with patch(
            "gsai.agents.tools.delete_file.safe_construct_path"
        ) as mock_safe_path:
            mock_safe_path.return_value = str(test_dir)
            result = delete_file(ctx, "test_directory")

        # Verify directory still exists and error was returned
        assert test_dir.exists()
        assert (
            result
            == "Error: Path is not a file (directories not supported): test_directory"
        )
