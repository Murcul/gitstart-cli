"""End-to-end integration tests for GitStart AI CLI."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
from loguru import logger
from typer.testing import CliRunner

from gsai.main import app


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows of the GitStart AI CLI."""

    def test_cli_status_command_basic(
        self, cli_runner: CliRunner, temp_dir: Path
    ) -> None:
        """Test basic status command execution in a temporary directory."""
        # Change to temp directory for the test
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            # Mock the API keys to avoid actual configuration requirements
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                result = cli_runner.invoke(app, ["status"])
                logger.info(result.stdout)
                # Basic assertions
                assert result.exit_code == 0
                assert "GitStart AI CLI Status" in result.stdout
                assert str(temp_dir)[0:20] in result.stdout
                assert "Working Directory" in result.stdout

        finally:
            os.chdir(original_cwd)

    def test_version_command(self, cli_runner: CliRunner) -> None:
        """Test version command execution."""
        result = cli_runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "GitStart AI CLI (gsai)" in result.stdout
        assert "Version: 0.0.12" in result.stdout

    def test_configure_command_with_invalid_approval_mode(
        self, cli_runner: CliRunner
    ) -> None:
        """Test configure command with invalid approval mode."""
        # The configure command no longer has --default-approval-mode option
        # Test with an invalid option instead
        result = cli_runner.invoke(
            app,
            ["configure", "--invalid-option"],
        )

        logger.info(result.exit_code)
        assert result.exit_code == 2  # Typer returns 2 for invalid options
        logger.info(result.stdout)
        assert "No such option" in result.stdout

    def test_configure_command_with_empty_api_keys(self, cli_runner: CliRunner) -> None:
        """Test configure command allows empty API keys without infinite loop."""
        result = cli_runner.invoke(
            app,
            ["configure"],
            input="\n\n",  # Press Enter twice to skip both API key prompts
        )

        logger.info(result.exit_code)
        assert result.exit_code == 0
        logger.info(result.stdout)
        assert "OpenAI API Key (leave empty to skip)" in result.stdout
        assert "Anthropic API Key (leave empty to skip)" in result.stdout
        # When no API keys are provided, no configuration changes are made
        assert "No configuration changes made." in result.stdout
        assert "Configuration saved to:" in result.stdout

    @pytest.mark.asyncio
    async def test_chat_command_security_validation(
        self, cli_runner: CliRunner
    ) -> None:
        """Test chat command with security validation for working directory."""
        # Test with a non-existent directory
        result = cli_runner.invoke(
            app,
            [
                "chat",
                "--working-dir",
                "/non/existent/path",
                "--approval-mode",
                "suggest",
            ],
        )

        # Should fail due to security validation
        assert result.exit_code == 1
        assert "Security Error" in result.stdout

    def test_help_functionality(self, cli_runner: CliRunner) -> None:
        """Test that help commands work correctly."""
        # Test main help
        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "GitStart AI CLI" in result.stdout
        assert "chat" in result.stdout
        assert "configure" in result.stdout
        assert "status" in result.stdout
        assert "version" in result.stdout

        # Test command-specific help
        result = cli_runner.invoke(app, ["chat", "--help"])
        assert result.exit_code == 0
        assert "Start an interactive AI coding session" in result.stdout
