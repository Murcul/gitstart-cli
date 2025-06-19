"""Tests for individual CLI commands."""

import os
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from gsai.main import app


class TestChatCommand:
    """Test the chat command functionality."""

    def test_chat_with_default_working_dir(self, cli_runner: CliRunner) -> None:
        """Test chat command uses current directory when no working dir specified."""
        with (
            patch("gsai.main.start_chat_session") as mock_chat,
            patch("gsai.main.validate_working_directory") as mock_validate,
        ):
            # Mock validation to return current directory
            mock_validate.return_value = os.getcwd()

            # Run the command
            _result = cli_runner.invoke(app, ["chat"])

            # Verify validation was called with current directory
            mock_validate.assert_called_once_with(os.getcwd())

            # Verify chat session was started with expected parameters (including verbose=False)
            mock_chat.assert_called_once_with(os.getcwd(), "suggest", False, False)

    def test_chat_with_custom_working_dir(
        self, cli_runner: CliRunner, temp_dir: Path
    ) -> None:
        """Test chat command with custom working directory."""
        with (
            patch("gsai.main.start_chat_session") as mock_chat,
            patch("gsai.main.validate_working_directory") as mock_validate,
        ):
            # Mock validation to return the temp directory
            mock_validate.return_value = str(temp_dir)

            # Run the command with custom working directory
            _result = cli_runner.invoke(app, ["chat", "--working-dir", str(temp_dir)])

            # Verify validation was called with the specified directory
            mock_validate.assert_called_once_with(str(temp_dir))

            # Verify chat session was started with the custom directory (including verbose=False)
            mock_chat.assert_called_once_with(str(temp_dir), "suggest", False, False)

    def test_chat_with_invalid_approval_mode(self, cli_runner: CliRunner) -> None:
        """Test chat command with invalid approval mode."""
        result = cli_runner.invoke(app, ["chat", "--approval-mode", "invalid"])

        # Should exit with error code 1
        assert result.exit_code == 1
        assert "Invalid approval mode" in result.stdout


class TestVersionCommand:
    """Test the version command functionality."""

    def test_version_command(self, cli_runner: CliRunner) -> None:
        """Test version command displays version information."""
        result = cli_runner.invoke(app, ["version"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should contain version information
        assert "GitStart AI CLI" in result.stdout
        assert "Version: 0.0.12" in result.stdout


class TestStatusCommand:
    """Test the status command functionality."""

    def test_status_includes_cache_info(self, cli_runner: CliRunner) -> None:
        """Test status command includes cache information."""
        result = cli_runner.invoke(app, ["status"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should contain cache information
        assert "Cache Enabled" in result.stdout
        assert "Cache Size" in result.stdout
        assert "Cache Entries" in result.stdout


class TestCacheCommands:
    """Test cache management commands."""

    def test_cache_status_command(self, cli_runner: CliRunner) -> None:
        """Test cache status command displays cache information."""
        result = cli_runner.invoke(app, ["cache-status"])

        # Should exit successfully
        assert result.exit_code == 0

        # Should contain cache status information
        assert "Repo Map Cache Status" in result.stdout
        assert "Cache Enabled" in result.stdout
        assert "Cache Directory" in result.stdout

    def test_cache_clear_command_cancelled(self, cli_runner: CliRunner) -> None:
        """Test cache clear command when user cancels."""
        # Simulate user saying 'no' to confirmation
        result = cli_runner.invoke(app, ["cache-clear"], input="n\n")

        # Should exit successfully
        assert result.exit_code == 0
        assert "Cache clear cancelled" in result.stdout

    def test_cache_clear_command_confirmed(self, cli_runner: CliRunner) -> None:
        """Test cache clear command when user confirms."""
        with patch("gsai.main.config_manager.clear_cache") as mock_clear:
            mock_clear.return_value = True

            # Simulate user saying 'yes' to confirmation
            result = cli_runner.invoke(app, ["cache-clear"], input="y\n")

            # Should exit successfully
            assert result.exit_code == 0
            assert "Cache cleared successfully" in result.stdout
            mock_clear.assert_called_once()

    def test_cache_clear_command_failure(self, cli_runner: CliRunner) -> None:
        """Test cache clear command when clearing fails."""
        with patch("gsai.main.config_manager.clear_cache") as mock_clear:
            mock_clear.return_value = False

            # Simulate user saying 'yes' to confirmation
            result = cli_runner.invoke(app, ["cache-clear"], input="y\n")

            # Should exit with error
            assert result.exit_code == 1
            assert "Failed to clear cache" in result.stdout
            mock_clear.assert_called_once()
