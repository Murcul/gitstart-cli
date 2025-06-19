"""Tests for CLI interface functionality."""

from typer.testing import CliRunner

from gsai.main import app


def test_version_command(cli_runner: CliRunner) -> None:
    """Test the version command displays version information."""
    result = cli_runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "GitStart AI CLI (gsai)" in result.stdout
    assert "Version: 0.0.12" in result.stdout


def test_status_command_with_current_dir(cli_runner: CliRunner) -> None:
    """Test the status command works with current directory."""
    result = cli_runner.invoke(app, ["status"])

    assert result.exit_code == 0
    assert "GitStart AI CLI Status" in result.stdout
    assert "Working Directory" in result.stdout
    assert "Cache Enabled" in result.stdout
