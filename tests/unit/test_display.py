"""Tests for the display wrapper functionality in the gsai module."""

import asyncio
import threading
import unittest
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from gsai.display_helpers import (
    ToolExecutionDisplay,
    get_current_display,
    tool_display_context,
    with_progress_display,
    with_progress_display_async,
)


class TestDisplayWrapper:
    """Test cases for display wrapper functionality."""

    def test_tool_execution_display_basic(self) -> None:
        """Test basic ToolExecutionDisplay functionality."""
        console = Console()
        display = ToolExecutionDisplay(console)

        # Test that display can be created
        assert display is not None
        assert display._tool_history == []

    def test_tool_display_context(self) -> None:
        """Test that tool_display_context correctly sets and clears the display."""
        mock_display = MagicMock()

        # Display should be None initially
        assert get_current_display() is None

        # Display should be set within the context
        with tool_display_context(mock_display):
            assert get_current_display() == mock_display

        # Display should be cleared after context
        assert get_current_display() is None

    def test_with_progress_display_decorator(self) -> None:
        """Test that the with_progress_display decorator works correctly."""
        mock_display = MagicMock()

        # Create a mock function to decorate
        @with_progress_display("test_tool", "Test operation")
        def test_function(x: int, y: int) -> int:
            return x + y

        # Function should work normally without display context
        result = test_function(2, 3)
        assert result == 5

        # Function should use display when context is available
        with tool_display_context(mock_display):
            result = test_function(2, 3)
            assert result == 5
            mock_display.show_tool_execution.assert_called_once()

    def test_threading_isolation(self) -> None:
        """Test that display contexts are isolated between threads."""
        import contextvars

        mock_display1 = MagicMock(name="display1")
        mock_display2 = MagicMock(name="display2")

        results = {}

        def thread_func(thread_id: int, display: MagicMock) -> None:
            with tool_display_context(display):
                # Store the current display in results
                results[thread_id] = get_current_display()
                # Wait to ensure threads overlap
                import time

                time.sleep(0.1)
                # Verify display is still correct
                assert get_current_display() == display

        # Create threads with context propagation
        def create_thread_with_context(
            target: Callable[..., Any], args: tuple[Any, ...]
        ) -> threading.Thread:
            ctx = contextvars.copy_context()

            def wrapper() -> None:
                ctx.run(target, *args)

            return threading.Thread(target=wrapper)

        # Start two threads with different displays, each with their own context
        with tool_display_context(mock_display1):
            t1 = create_thread_with_context(thread_func, (1, mock_display1))

        with tool_display_context(mock_display2):
            t2 = create_thread_with_context(thread_func, (2, mock_display2))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Verify each thread got its own display
        assert results[1] == mock_display1
        assert results[2] == mock_display2

        # Main thread's display should still be None
        assert get_current_display() is None

    def test_with_progress_display_different_tools(self) -> None:
        """Test that decorator works with different tool names."""
        mock_display = MagicMock()

        # Create a function with a known tool
        @with_progress_display("view_file", "Test operation")
        def test_function_known() -> str:
            return "result"

        # Create a function with an unknown tool
        @with_progress_display("unknown_tool", "Test operation")
        def test_function_unknown() -> str:
            return "result"

        with tool_display_context(mock_display):
            # Both functions should show progress when display context is available
            test_function_known()
            mock_display.show_tool_execution.assert_called_once()

            # Reset mock
            mock_display.reset_mock()

            test_function_unknown()
            mock_display.show_tool_execution.assert_called_once()

    def test_with_progress_display_error_handling(self) -> None:
        """Test that decorator handles errors during tool execution."""
        mock_display = MagicMock()

        @with_progress_display("test_tool", "Test operation")
        def failing_function() -> None:
            raise ValueError("Test error")

        with tool_display_context(mock_display):
            with pytest.raises(ValueError, match="Test error"):
                failing_function()
            # Display should still be called even if function fails
            mock_display.show_tool_execution.assert_called_once()

    @pytest.mark.asyncio
    async def test_with_progress_display_async(self) -> None:
        """Test that the async progress display decorator works correctly."""
        mock_display = MagicMock()

        @with_progress_display_async("test_tool", "Test async operation")
        async def async_test_function(x: int, y: int) -> int:
            await asyncio.sleep(0.01)  # Simulate async work
            return x + y

        # Function should work normally without display context
        result = await async_test_function(2, 3)
        assert result == 5

        # Function should use display when context is available
        with tool_display_context(mock_display):
            result = await async_test_function(2, 3)
            assert result == 5
            mock_display.show_tool_execution.assert_called_once()

    @pytest.mark.asyncio
    async def test_with_progress_display_async_different_tools(self) -> None:
        """Test that async decorator works with different tool names."""
        mock_display = MagicMock()

        @with_progress_display_async("view_file", "Test operation")
        async def async_function_known() -> str:
            return "result"

        @with_progress_display_async("unknown_tool", "Test operation")
        async def async_function_unknown() -> str:
            return "result"

        with tool_display_context(mock_display):
            # Both functions should show progress when display context is available
            await async_function_known()
            mock_display.show_tool_execution.assert_called_once()

            # Reset mock
            mock_display.reset_mock()

            await async_function_unknown()
            mock_display.show_tool_execution.assert_called_once()

    @pytest.mark.asyncio
    async def test_with_progress_display_async_error_handling(self) -> None:
        """Test that async decorator handles errors during tool execution."""
        mock_display = MagicMock()

        @with_progress_display_async("test_tool", "Test async operation")
        async def async_failing_function() -> None:
            raise ValueError("Test async error")

        with tool_display_context(mock_display):
            with pytest.raises(ValueError, match="Test async error"):
                await async_failing_function()
            # Display should still be called even if function fails
            mock_display.show_tool_execution.assert_called_once()

    def test_display_context_cleanup_on_exception(self) -> None:
        """Test that display context is properly cleaned up when exceptions occur."""
        mock_display = MagicMock()

        try:
            with tool_display_context(mock_display):
                assert get_current_display() == mock_display
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Display should be cleaned up even after exception
        assert get_current_display() is None

    def test_get_current_display_thread_safety(self) -> None:
        """Test that get_current_display is thread-safe."""
        import contextvars

        mock_display = MagicMock()
        results = {}
        errors = []

        def thread_func(thread_id: int) -> None:
            try:
                # Each thread should start with no display
                assert get_current_display() is None
                results[f"{thread_id}_start"] = get_current_display()

                with tool_display_context(mock_display):
                    # Each thread should see its own display
                    results[f"{thread_id}_context"] = get_current_display()

                # Each thread should end with no display
                results[f"{thread_id}_end"] = get_current_display()
            except Exception as e:
                errors.append(f"Thread {thread_id}: {e}")

        # Create threads with context propagation
        def create_thread_with_context(
            target: Callable[..., Any], args: tuple[Any, ...]
        ) -> threading.Thread:
            ctx = contextvars.copy_context()

            def wrapper() -> None:
                ctx.run(target, *args)

            return threading.Thread(target=wrapper)

        # Start multiple threads
        threads = []
        for i in range(5):
            t = create_thread_with_context(thread_func, (i,))
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Check for any errors
        assert not errors, f"Thread errors: {errors}"

        # Verify all threads behaved correctly
        for i in range(5):
            assert results[f"{i}_start"] is None
            assert results[f"{i}_context"] == mock_display
            assert results[f"{i}_end"] is None


class TestDisplayWrapperEdgeCases:
    """Test edge cases and error scenarios for display wrapper."""

    def test_decorator_without_display_context(self) -> None:
        """Test that decorators work correctly when no display context is set."""

        @with_progress_display("test_tool", "Test operation")
        def test_function() -> str:
            return "success"

        # Should work normally without any display context
        result = test_function()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_async_decorator_without_display_context(self) -> None:
        """Test that async decorators work correctly when no display context is set."""

        @with_progress_display_async("test_tool", "Test operation")
        async def async_test_function() -> str:
            await asyncio.sleep(0.001)
            return "success"

        # Should work normally without any display context
        result = await async_test_function()
        assert result == "success"

    def test_nested_display_contexts(self) -> None:
        """Test behavior with nested display contexts."""
        mock_display1 = MagicMock(name="display1")
        mock_display2 = MagicMock(name="display2")

        with tool_display_context(mock_display1):
            assert get_current_display() == mock_display1

            with tool_display_context(mock_display2):
                assert get_current_display() == mock_display2

            # Should return to first display after inner context
            assert get_current_display() == mock_display1

        # Should be None after all contexts
        assert get_current_display() is None

    def test_display_context_with_none(self) -> None:
        """Test that display context handles None display gracefully."""
        with tool_display_context(None):  # type: ignore[arg-type]
            assert get_current_display() is None

    def test_concurrent_tool_executions(self) -> None:
        """Test that multiple tools can execute concurrently with progress display."""
        import contextvars

        mock_display = MagicMock()
        results = {}
        errors = []

        @with_progress_display("concurrent_tool", "Concurrent operation")
        def concurrent_function(thread_id: int) -> str:
            import time

            time.sleep(0.1)  # Simulate work
            return f"result_{thread_id}"

        def thread_func(thread_id: int) -> None:
            try:
                with tool_display_context(mock_display):
                    result = concurrent_function(thread_id)
                    results[thread_id] = result
            except Exception as e:
                errors.append(f"Thread {thread_id}: {e}")

        # Create threads with context propagation
        def create_thread_with_context(
            target: Callable[..., Any], args: tuple[Any, ...]
        ) -> threading.Thread:
            ctx = contextvars.copy_context()

            def wrapper() -> None:
                ctx.run(target, *args)

            return threading.Thread(target=wrapper)

        # Start multiple threads
        threads = []
        for i in range(3):
            t = create_thread_with_context(thread_func, (i,))
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Check for any errors
        assert not errors, f"Thread errors: {errors}"

        # Verify all threads completed successfully
        for i in range(3):
            assert results[i] == f"result_{i}"

        # Display should have been called for each thread
        assert mock_display.show_tool_execution.call_count == 3


class TestToolExecutionDisplay:
    """Test cases for ToolExecutionDisplay class methods."""

    def test_show_tool_execution_context_manager(self) -> None:
        """Test that show_tool_execution works as a context manager."""
        console = Console()
        display = ToolExecutionDisplay(console)

        # Mock console.print to capture output
        with patch.object(console, "print") as mock_print:
            with display.show_tool_execution("test_tool", "Testing"):
                pass

            # Should have printed completion message (start message only for agentic tools)
            assert mock_print.call_count == 1
            end_call = mock_print.call_args_list[0][0][0]

            assert "✅" in end_call and "Test Tool Complete" in end_call
            # Check that tool was added to history with tuple format
            assert len(display._tool_history) == 1
            assert display._tool_history[0][0] == "test_tool"
            assert display._tool_history[0][1] == "completed"

    def test_show_tool_execution_error_handling(self) -> None:
        """Test that show_tool_execution handles errors during execution."""

        console = Console()
        display = ToolExecutionDisplay(console)

        # Mock console.print to capture output
        with patch.object(console, "print") as mock_print:
            try:
                with display.show_tool_execution("test_tool", "Testing"):
                    raise ValueError("Test error")
            except ValueError:
                pass

            # Should have printed error message (start message only for agentic tools)
            assert mock_print.call_count == 1
            error_call = mock_print.call_args_list[0][0][0]

            assert "❌" in error_call and "Test Tool Failed" in error_call
            # Check that tool was added to history with tuple format
            assert len(display._tool_history) == 1
            assert display._tool_history[0][0] == "test_tool"
            assert display._tool_history[0][1] == "failed"


if __name__ == "__main__":
    unittest.main()
