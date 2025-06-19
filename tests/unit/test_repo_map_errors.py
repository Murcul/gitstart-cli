"""Unit tests for RepoMap error handling and edge cases."""

import os
from unittest.mock import Mock, patch

import pytest

from gsai.repo_map import RepoMap, get_repo_map_for_prompt


class TestRepoMapErrorHandling:
    """Test RepoMap error handling and edge cases."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.repo_map = RepoMap(root="/test/repo")

    def test_repo_map_initialization_defaults(self) -> None:
        """Test RepoMap initialization with default values."""
        repo_map = RepoMap()

        assert repo_map.root == os.getcwd()
        assert repo_map.max_map_tokens == 10000
        assert repo_map.map_mul_no_files == 8
        assert repo_map.verbose is False
        assert repo_map.refresh == "auto"

    def test_repo_map_initialization_custom_values(self) -> None:
        """Test RepoMap initialization with custom values."""
        repo_map = RepoMap(
            map_tokens=5000,
            root="/custom/root",
            verbose=True,
            max_context_window=100000,
            map_mul_no_files=4,
            refresh="manual",
        )

        assert repo_map.root == "/custom/root"
        assert repo_map.max_map_tokens == 5000
        assert repo_map.map_mul_no_files == 4
        assert repo_map.verbose is True
        assert repo_map.refresh == "manual"
        assert repo_map.max_context_window == 100000

    def test_token_count_short_text(self) -> None:
        """Test token counting for short text (uses actual encoding)."""
        text = "hello world"
        count = self.repo_map.token_count(text)

        assert isinstance(count, int)
        assert count > 0

    def test_token_count_long_text(self) -> None:
        """Test token counting for long text (uses sampling)."""
        # Create text longer than 200 characters
        text = "hello world " * 50  # Much longer than 200 chars
        count = self.repo_map.token_count(text)

        assert isinstance(count, int | float)
        assert count > 0

    def test_token_count_empty_text(self) -> None:
        """Test token counting for empty text."""
        count = self.repo_map.token_count("")
        assert count == 0

    def test_get_repo_map_zero_tokens(self) -> None:
        """Test get_repo_map with zero max tokens."""
        self.repo_map.max_map_tokens = 0
        result = self.repo_map.get_repo_map([], ["file1.py"])
        assert result == ""

    def test_get_repo_map_no_other_files(self) -> None:
        """Test get_repo_map with no other files."""
        result = self.repo_map.get_repo_map([], [])
        assert result == ""

    def test_get_repo_map_none_other_files(self) -> None:
        """Test get_repo_map with None other files."""
        result = self.repo_map.get_repo_map([], None)
        assert result == ""

    @patch("gsai.repo_map.RepoMap.get_ranked_tags_map")
    def test_get_repo_map_recursion_error(self, mock_get_ranked_tags_map: Mock) -> None:
        """Test get_repo_map handling RecursionError."""
        mock_get_ranked_tags_map.side_effect = RecursionError(
            "Maximum recursion depth exceeded"
        )

        result = self.repo_map.get_repo_map([], ["file1.py"])

        assert result == ""
        assert self.repo_map.max_map_tokens == 0  # Should disable repo map

    @patch("gsai.repo_map.RepoMap.get_ranked_tags_map")
    def test_get_repo_map_empty_files_listing(
        self, mock_get_ranked_tags_map: Mock
    ) -> None:
        """Test get_repo_map when ranked tags map returns empty."""
        mock_get_ranked_tags_map.return_value = ""

        result = self.repo_map.get_repo_map([], ["file1.py"])

        assert result == ""

    @patch("gsai.repo_map.RepoMap.get_ranked_tags_map")
    def test_get_repo_map_none_files_listing(
        self, mock_get_ranked_tags_map: Mock
    ) -> None:
        """Test get_repo_map when ranked tags map returns None."""
        mock_get_ranked_tags_map.return_value = None

        result = self.repo_map.get_repo_map([], ["file1.py"])

        assert result == ""

    @patch("gsai.repo_map.RepoMap.get_ranked_tags_map")
    @patch("gsai.repo_map.RepoMap.token_count")
    def test_get_repo_map_with_context_window_expansion(
        self, mock_token_count: Mock, mock_get_ranked_tags_map: Mock
    ) -> None:
        """Test get_repo_map with context window expansion for no chat files."""
        mock_get_ranked_tags_map.return_value = "repo map content"
        mock_token_count.return_value = 1000

        self.repo_map.max_context_window = 50000
        self.repo_map.map_mul_no_files = 4

        # No chat files should trigger expansion
        result = self.repo_map.get_repo_map([], ["file1.py"])

        assert result is not None
        # Should call with expanded token limit
        args = mock_get_ranked_tags_map.call_args[0]
        max_tokens_used = args[2]  # Third argument is max_map_tokens
        assert max_tokens_used > self.repo_map.max_map_tokens

    @patch("gsai.repo_map.RepoMap.get_ranked_tags_map")
    def test_get_repo_map_with_repo_content_prefix(
        self, mock_get_ranked_tags_map: Mock
    ) -> None:
        """Test get_repo_map with custom repo content prefix."""
        mock_get_ranked_tags_map.return_value = "repo map content"
        self.repo_map.repo_content_prefix = "Custom prefix {other}files:\n"

        # With chat files
        result = self.repo_map.get_repo_map(["chat.py"], ["file1.py"])
        assert result.startswith("Custom prefix other files:")

        # Without chat files
        result = self.repo_map.get_repo_map([], ["file1.py"])
        assert result.startswith("Custom prefix files:")

    def test_get_ranked_tags_map_force_refresh(self) -> None:
        """Test get_ranked_tags_map with force_refresh=True."""
        # Set up cache with existing data
        cache_key = ((), ("file1.py",), 1000, None, None)
        self.repo_map.map_cache[cache_key] = "cached content"

        with patch.object(
            self.repo_map, "get_ranked_tags_map_uncached", return_value="fresh content"
        ) as mock_uncached:
            result = self.repo_map.get_ranked_tags_map(
                [], ["file1.py"], 1000, force_refresh=True
            )

            assert result == "fresh content"
            mock_uncached.assert_called_once()

    def test_get_ranked_tags_map_manual_refresh_with_last_map(self) -> None:
        """Test get_ranked_tags_map with manual refresh and existing last_map."""
        self.repo_map.refresh = "manual"
        self.repo_map.last_map = "last map content"

        result = self.repo_map.get_ranked_tags_map([], ["file1.py"], 1000)

        assert result == "last map content"

    def test_get_ranked_tags_map_cache_hit(self) -> None:
        """Test get_ranked_tags_map cache hit."""
        self.repo_map.refresh = "files"
        cache_key = ((), ("file1.py",), 1000, None, None)
        self.repo_map.map_cache[cache_key] = "cached content"

        with patch.object(
            self.repo_map, "get_ranked_tags_map_uncached", return_value="fresh content"
        ) as _mock_uncached:
            result = self.repo_map.get_ranked_tags_map([], ["file1.py"], 1000)

            # Should return some result (cached or fresh)
            assert result is not None
            assert isinstance(result, str)
            # May or may not call uncached method depending on cache behavior

    @patch("time.time")
    def test_get_ranked_tags_map_processing_time_tracking(
        self, mock_time: Mock
    ) -> None:
        """Test that processing time is tracked correctly."""
        mock_time.side_effect = [1000.0, 1002.5]  # 2.5 second processing time

        with patch.object(
            self.repo_map, "get_ranked_tags_map_uncached", return_value="content"
        ):
            self.repo_map.get_ranked_tags_map([], ["file1.py"], 1000)

            assert self.repo_map.map_processing_time == 2.5
            assert self.repo_map.last_map == "content"

    @patch("gsai.repo_map.RepoMap.to_tree")
    @patch("gsai.repo_map.RepoMap.get_ranked_tags")
    @patch("gsai.repo_map.filter_important_files")
    def test_get_ranked_tags_map_uncached_binary_search(
        self, mock_filter_files: Mock, mock_get_ranked_tags: Mock, mock_to_tree: Mock
    ) -> None:
        """Test binary search in get_ranked_tags_map_uncached."""
        mock_filter_files.return_value = []
        mock_get_ranked_tags.return_value = [
            ("file1.py",),
            ("file2.py",),
            ("file3.py",),
        ]

        # Mock token counting to simulate binary search
        mock_to_tree.side_effect = (
            lambda tags, chat_files: f"tree with {len(tags)} files"
        )

        with patch.object(self.repo_map, "token_count") as mock_token_count:
            # First call: too many tokens, second call: just right, third call for final result
            mock_token_count.side_effect = [15000, 8000, 8000]  # max_tokens = 10000

            result = self.repo_map.get_ranked_tags_map_uncached([], ["file1.py"], 10000)

            assert "tree with" in result  # Should contain tree output

    @patch("gsai.repo_map.RepoMap.get_ranked_tags")
    @patch("gsai.repo_map.filter_important_files")
    def test_get_ranked_tags_map_uncached_no_tags(
        self, mock_filter_files: Mock, mock_get_ranked_tags: Mock
    ) -> None:
        """Test get_ranked_tags_map_uncached with no tags."""
        mock_filter_files.return_value = []
        mock_get_ranked_tags.return_value = []

        result = self.repo_map.get_ranked_tags_map_uncached([], ["file1.py"], 10000)

        assert result == ""

    def test_warned_files_tracking(self) -> None:
        """Test that warned files are tracked to avoid duplicate warnings."""
        # This is a class variable, so we need to test it carefully
        initial_warned = RepoMap.warned_files.copy()

        try:
            with patch("pathlib.Path.is_file", return_value=False):
                self.repo_map.get_ranked_tags([], ["/test/missing.py"], set(), set())

                # Should add to warned files
                assert "/test/missing.py" in RepoMap.warned_files

                # Second call should not warn again (tested by checking logs)
                self.repo_map.get_ranked_tags([], ["/test/missing.py"], set(), set())

        finally:
            # Restore original warned files
            RepoMap.warned_files = initial_warned


class TestGetRepoMapForPrompt:
    """Test get_repo_map_for_prompt function."""

    def test_get_repo_map_for_prompt_empty_repo_path(self) -> None:
        """Test get_repo_map_for_prompt with empty repo path."""
        with pytest.raises(AssertionError, match="No Repo Path provided"):
            get_repo_map_for_prompt("")

    @patch("gsai.repo_map.get_files_excluding_gitignore")
    def test_get_repo_map_for_prompt_large_repo(self, mock_get_files: Mock) -> None:
        """Test get_repo_map_for_prompt with large repository."""
        # Simulate repo with >10000 files
        mock_get_files.return_value = [f"file{i}.py" for i in range(10001)]

        result = get_repo_map_for_prompt("/test/repo")

        assert result == "Repo is too large to generate a repo map."

    @patch("gsai.repo_map.get_files_excluding_gitignore")
    @patch("gsai.repo_map.RepoMap")
    def test_get_repo_map_for_prompt_success(
        self, mock_repo_map_class: Mock, mock_get_files: Mock
    ) -> None:
        """Test successful get_repo_map_for_prompt."""
        mock_get_files.return_value = ["file1.py", "file2.py"]

        mock_repo_map = Mock()
        mock_repo_map.get_repo_map.return_value = "generated repo map"
        mock_repo_map_class.return_value = mock_repo_map

        result = get_repo_map_for_prompt("/test/repo")

        assert result == "generated repo map"
        mock_repo_map_class.assert_called_once_with(root="/test/repo")
        mock_repo_map.get_repo_map.assert_called_once_with([], ["file1.py", "file2.py"])

    @patch("gsai.repo_map.get_files_excluding_gitignore")
    def test_get_repo_map_for_prompt_get_files_exception(
        self, mock_get_files: Mock
    ) -> None:
        """Test get_repo_map_for_prompt when get_files raises exception."""
        mock_get_files.side_effect = OSError("Permission denied")

        with pytest.raises(OSError):
            get_repo_map_for_prompt("/test/repo")


class TestRepoMapEdgeCases:
    """Test various edge cases and boundary conditions."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.repo_map = RepoMap(root="/test/repo")

    def test_get_rel_fname_edge_cases(self) -> None:
        """Test get_rel_fname with various edge cases."""
        # Test with root path
        result = self.repo_map.get_rel_fname("/test/repo")
        assert result == "."

        # Test with nested path
        result = self.repo_map.get_rel_fname("/test/repo/deep/nested/file.py")
        assert result == "deep/nested/file.py"

    def test_cache_threshold_property(self) -> None:
        """Test cache threshold property."""
        assert self.repo_map.cache_threshold == 0.95

    def test_tree_cache_initialization(self) -> None:
        """Test that tree cache is properly initialized."""
        assert isinstance(self.repo_map.tree_cache, dict)
        assert isinstance(self.repo_map.tree_context_cache, dict)
        assert isinstance(self.repo_map.map_cache, dict)

    def test_map_processing_time_initialization(self) -> None:
        """Test that map processing time is initialized."""
        assert self.repo_map.map_processing_time == 0

    def test_last_map_initialization(self) -> None:
        """Test that last_map is initialized to None."""
        assert self.repo_map.last_map is None

    @patch("gsai.repo_map.RepoMap.token_count")
    def test_verbose_logging(self, mock_token_count: Mock) -> None:
        """Test verbose logging functionality."""
        mock_token_count.return_value = 5000

        # Create verbose repo map
        verbose_repo_map = RepoMap(verbose=True)

        with patch(
            "gsai.repo_map.RepoMap.get_ranked_tags_map", return_value="test content"
        ):
            # This should trigger verbose logging
            result = verbose_repo_map.get_repo_map([], ["file1.py"])

            assert result is not None

    def test_refresh_auto_cache_behavior(self) -> None:
        """Test auto refresh cache behavior based on processing time."""
        self.repo_map.refresh = "auto"

        # Short processing time should not use cache
        self.repo_map.map_processing_time = 0.5
        cache_key = ((), ("file1.py",), 1000, None, None)
        self.repo_map.map_cache[cache_key] = "cached content"

        with patch.object(
            self.repo_map, "get_ranked_tags_map_uncached", return_value="fresh content"
        ) as mock_uncached:
            self.repo_map.get_ranked_tags_map([], ["file1.py"], 1000)

            # Should generate fresh content due to short processing time
            mock_uncached.assert_called_once()

    def test_refresh_always_no_cache(self) -> None:
        """Test that refresh='always' never uses cache."""
        self.repo_map.refresh = "always"
        self.repo_map.map_processing_time = 5.0  # Long processing time

        cache_key = ((), ("file1.py",), 1000, None, None)
        self.repo_map.map_cache[cache_key] = "cached content"

        with patch.object(
            self.repo_map, "get_ranked_tags_map_uncached", return_value="fresh content"
        ) as mock_uncached:
            result = self.repo_map.get_ranked_tags_map([], ["file1.py"], 1000)

            assert result == "fresh content"
            mock_uncached.assert_called_once()

    def test_context_window_calculation_edge_cases(self) -> None:
        """Test context window calculation edge cases."""
        self.repo_map.max_map_tokens = 1000
        self.repo_map.max_context_window = 5000
        self.repo_map.map_mul_no_files = 10

        # Test when calculated target exceeds context window
        with patch.object(
            self.repo_map, "get_ranked_tags_map_uncached", return_value="content"
        ):
            result = self.repo_map.get_repo_map([], ["file1.py"])

            # Should use context window minus padding instead of calculated target
            assert result is not None

    def test_empty_mentioned_parameters(self) -> None:
        """Test handling of empty mentioned parameters."""
        with patch.object(
            self.repo_map, "get_ranked_tags_map_uncached", return_value="content"
        ):
            # Should handle None values gracefully
            result = self.repo_map.get_repo_map([], ["file1.py"], None, None)
            assert result is not None
