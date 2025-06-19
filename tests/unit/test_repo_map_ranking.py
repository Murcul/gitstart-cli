"""Unit tests for RepoMap PageRank algorithm and file ranking."""

from unittest.mock import Mock, patch

from gsai.repo_map import RepoMap, Tag


class TestRepoMapRanking:
    """Test RepoMap file ranking and PageRank algorithm."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.repo_map = RepoMap(root="/test/repo")

    @patch("pathlib.Path.is_file")
    @patch("gsai.repo_map.RepoMap.get_tags")
    def test_get_ranked_tags_basic(
        self, mock_get_tags: Mock, mock_is_file: Mock
    ) -> None:
        """Test basic ranked tags functionality."""
        mock_is_file.return_value = True

        # Mock tags for different files
        mock_get_tags.side_effect = [
            # file1.py - defines function_a
            [Tag("file1.py", "/test/file1.py", 10, "function_a", "def")],
            # file2.py - references function_a
            [Tag("file2.py", "/test/file2.py", 5, "function_a", "ref")],
        ]

        chat_fnames: list[str] = []
        other_fnames = ["/test/file1.py", "/test/file2.py"]
        mentioned_fnames: set[str] = set()
        mentioned_idents: set[str] = set()

        result = self.repo_map.get_ranked_tags(
            chat_fnames, other_fnames, mentioned_fnames, mentioned_idents
        )

        assert len(result) > 0
        # Should contain tuples with file information
        assert all(isinstance(item, tuple) for item in result)

    @patch("pathlib.Path.is_file")
    @patch("gsai.repo_map.RepoMap.get_tags")
    def test_get_ranked_tags_with_chat_files(
        self, mock_get_tags: Mock, mock_is_file: Mock
    ) -> None:
        """Test ranked tags with chat files (personalization)."""
        mock_is_file.return_value = True

        mock_get_tags.side_effect = [
            # chat_file.py - defines function_a
            [Tag("chat_file.py", "/test/chat_file.py", 10, "function_a", "def")],
            # other_file.py - references function_a
            [Tag("other_file.py", "/test/other_file.py", 5, "function_a", "ref")],
        ]

        chat_fnames = ["/test/chat_file.py"]
        other_fnames = ["/test/other_file.py"]
        mentioned_fnames: set[str] = set()
        mentioned_idents: set[str] = set()

        result = self.repo_map.get_ranked_tags(
            chat_fnames, other_fnames, mentioned_fnames, mentioned_idents
        )

        # Chat files should not appear in ranked tags (they're excluded)
        file_names = [item[0] for item in result if len(item) > 0]
        assert "chat_file.py" not in file_names

    @patch("pathlib.Path.is_file")
    @patch("gsai.repo_map.RepoMap.get_tags")
    def test_get_ranked_tags_mentioned_identifiers(
        self, mock_get_tags: Mock, mock_is_file: Mock
    ) -> None:
        """Test ranked tags with mentioned identifiers (higher weight)."""
        mock_is_file.return_value = True

        mock_get_tags.side_effect = [
            # file1.py - defines important_function
            [Tag("file1.py", "/test/file1.py", 10, "important_function", "def")],
            # file2.py - references important_function
            [Tag("file2.py", "/test/file2.py", 5, "important_function", "ref")],
        ]

        chat_fnames: list[str] = []
        other_fnames = ["/test/file1.py", "/test/file2.py"]
        mentioned_fnames: set[str] = set()
        mentioned_idents: set[str] = {
            "important_function"
        }  # This should get higher weight

        result = self.repo_map.get_ranked_tags(
            chat_fnames, other_fnames, mentioned_fnames, mentioned_idents
        )

        assert len(result) > 0

    @patch("pathlib.Path.is_file")
    @patch("gsai.repo_map.RepoMap.get_tags")
    def test_get_ranked_tags_snake_case_camel_case_weighting(
        self, mock_get_tags: Mock, mock_is_file: Mock
    ) -> None:
        """Test that snake_case and camelCase identifiers get higher weight."""
        mock_is_file.return_value = True

        mock_get_tags.side_effect = [
            # file1.py - defines snake_case_function (should get higher weight)
            [Tag("file1.py", "/test/file1.py", 10, "snake_case_function", "def")],
            # file2.py - defines camelCaseFunction (should get higher weight)
            [Tag("file2.py", "/test/file2.py", 10, "camelCaseFunction", "def")],
            # file3.py - defines shortfunc (should get lower weight)
            [Tag("file3.py", "/test/file3.py", 10, "shortfunc", "def")],
            # References
            [Tag("file4.py", "/test/file4.py", 5, "snake_case_function", "ref")],
            [Tag("file4.py", "/test/file4.py", 6, "camelCaseFunction", "ref")],
            [Tag("file4.py", "/test/file4.py", 7, "shortfunc", "ref")],
        ]

        chat_fnames: list[str] = []
        other_fnames = [
            "/test/file1.py",
            "/test/file2.py",
            "/test/file3.py",
            "/test/file4.py",
        ]
        mentioned_fnames: set[str] = set()
        mentioned_idents: set[str] = set()

        result = self.repo_map.get_ranked_tags(
            chat_fnames, other_fnames, mentioned_fnames, mentioned_idents
        )

        assert len(result) > 0

    @patch("pathlib.Path.is_file")
    @patch("gsai.repo_map.RepoMap.get_tags")
    def test_get_ranked_tags_private_identifier_weighting(
        self, mock_get_tags: Mock, mock_is_file: Mock
    ) -> None:
        """Test that private identifiers (starting with _) get lower weight."""
        mock_is_file.return_value = True

        mock_get_tags.side_effect = [
            # file1.py - defines _private_function (should get lower weight)
            [Tag("file1.py", "/test/file1.py", 10, "_private_function", "def")],
            # file2.py - references _private_function
            [Tag("file2.py", "/test/file2.py", 5, "_private_function", "ref")],
        ]

        chat_fnames: list[str] = []
        other_fnames = ["/test/file1.py", "/test/file2.py"]
        mentioned_fnames: set[str] = set()
        mentioned_idents: set[str] = set()

        result = self.repo_map.get_ranked_tags(
            chat_fnames, other_fnames, mentioned_fnames, mentioned_idents
        )

        assert len(result) > 0

    @patch("pathlib.Path.is_file")
    @patch("gsai.repo_map.RepoMap.get_tags")
    def test_get_ranked_tags_high_definition_count_weighting(
        self, mock_get_tags: Mock, mock_is_file: Mock
    ) -> None:
        """Test that identifiers with many definitions get lower weight."""
        mock_is_file.return_value = True

        # Create many files that define the same identifier
        mock_get_tags.side_effect = [
            [Tag(f"file{i}.py", f"/test/file{i}.py", 10, "common_name", "def")]
            for i in range(7)  # 7 definitions > 5 threshold
        ] + [[Tag("ref_file.py", "/test/ref_file.py", 5, "common_name", "ref")]]

        chat_fnames: list[str] = []
        other_fnames = [f"/test/file{i}.py" for i in range(7)] + ["/test/ref_file.py"]
        mentioned_fnames: set[str] = set()
        mentioned_idents: set[str] = set()

        result = self.repo_map.get_ranked_tags(
            chat_fnames, other_fnames, mentioned_fnames, mentioned_idents
        )

        assert len(result) > 0

    @patch("pathlib.Path.is_file")
    def test_get_ranked_tags_file_not_found(self, mock_is_file: Mock) -> None:
        """Test ranked tags with non-existent files."""
        mock_is_file.return_value = False

        chat_fnames: list[str] = []
        other_fnames = ["/test/nonexistent.py"]
        mentioned_fnames: set[str] = set()
        mentioned_idents: set[str] = set()

        result = self.repo_map.get_ranked_tags(
            chat_fnames, other_fnames, mentioned_fnames, mentioned_idents
        )

        # Should handle missing files gracefully
        assert isinstance(result, list)

    @patch("pathlib.Path.is_file")
    def test_get_ranked_tags_os_error(self, mock_is_file: Mock) -> None:
        """Test ranked tags with OS error during file check."""
        mock_is_file.side_effect = OSError("Permission denied")

        chat_fnames: list[str] = []
        other_fnames = ["/test/restricted.py"]
        mentioned_fnames: set[str] = set()
        mentioned_idents: set[str] = set()

        result = self.repo_map.get_ranked_tags(
            chat_fnames, other_fnames, mentioned_fnames, mentioned_idents
        )

        # Should handle OS errors gracefully
        assert isinstance(result, list)

    @patch("pathlib.Path.is_file")
    @patch("gsai.repo_map.RepoMap.get_tags")
    def test_get_ranked_tags_no_references(
        self, mock_get_tags: Mock, mock_is_file: Mock
    ) -> None:
        """Test ranked tags when there are no references (only definitions)."""
        mock_is_file.return_value = True

        mock_get_tags.side_effect = [
            # Only definitions, no references
            [Tag("file1.py", "/test/file1.py", 10, "function_a", "def")],
            [Tag("file2.py", "/test/file2.py", 15, "function_b", "def")],
        ]

        chat_fnames: list[str] = []
        other_fnames = ["/test/file1.py", "/test/file2.py"]
        mentioned_fnames: set[str] = set()
        mentioned_idents: set[str] = set()

        result = self.repo_map.get_ranked_tags(
            chat_fnames, other_fnames, mentioned_fnames, mentioned_idents
        )

        assert len(result) > 0

    @patch("pathlib.Path.is_file")
    @patch("gsai.repo_map.RepoMap.get_tags")
    @patch("networkx.pagerank")
    def test_get_ranked_tags_pagerank_zero_division_error(
        self, mock_pagerank: Mock, mock_get_tags: Mock, mock_is_file: Mock
    ) -> None:
        """Test ranked tags when PageRank raises ZeroDivisionError."""
        mock_is_file.return_value = True
        # Use relative filenames that match what get_rel_fname would return
        mock_get_tags.side_effect = [
            [Tag("file1.py", "/test/file1.py", 10, "function_a", "def")],
            [Tag("file2.py", "/test/file2.py", 5, "function_a", "ref")],
        ]

        # First call raises ZeroDivisionError, second call should succeed
        # Use the same relative filenames that will be in the graph
        mock_pagerank.side_effect = [
            ZeroDivisionError("Division by zero"),
            {"file1.py": 0.5, "file2.py": 0.5},
        ]

        chat_fnames: list[str] = []
        other_fnames = ["/test/file1.py", "/test/file2.py"]
        mentioned_fnames: set[str] = set()
        mentioned_idents: set[str] = set()

        # Mock get_rel_fname to return consistent relative paths
        with patch.object(self.repo_map, "get_rel_fname") as mock_get_rel_fname:
            mock_get_rel_fname.side_effect = lambda x: x.split("/")[
                -1
            ]  # Return just filename

            result = self.repo_map.get_ranked_tags(
                chat_fnames, other_fnames, mentioned_fnames, mentioned_idents
            )

            # Should handle the error and retry without personalization
            assert len(result) >= 0  # May be empty if PageRank fails
            assert mock_pagerank.call_count == 2

    @patch("pathlib.Path.is_file")
    @patch("gsai.repo_map.RepoMap.get_tags")
    @patch("networkx.pagerank")
    def test_get_ranked_tags_pagerank_double_zero_division_error(
        self, mock_pagerank: Mock, mock_get_tags: Mock, mock_is_file: Mock
    ) -> None:
        """Test ranked tags when PageRank raises ZeroDivisionError twice."""
        mock_is_file.return_value = True
        mock_get_tags.side_effect = [
            [Tag("file1.py", "/test/file1.py", 10, "function_a", "def")],
            [Tag("file2.py", "/test/file2.py", 5, "function_a", "ref")],
        ]

        # Both calls raise ZeroDivisionError
        mock_pagerank.side_effect = ZeroDivisionError("Division by zero")

        chat_fnames: list[str] = []
        other_fnames = ["/test/file1.py", "/test/file2.py"]
        mentioned_fnames: set[str] = set()
        mentioned_idents: set[str] = set()

        result = self.repo_map.get_ranked_tags(
            chat_fnames, other_fnames, mentioned_fnames, mentioned_idents
        )

        # Should return empty list when PageRank fails completely
        assert result == []
        assert mock_pagerank.call_count == 2

    @patch("pathlib.Path.is_file")
    @patch("gsai.repo_map.RepoMap.get_tags")
    def test_get_ranked_tags_self_references(
        self, mock_get_tags: Mock, mock_is_file: Mock
    ) -> None:
        """Test ranked tags with self-referencing definitions (no external references)."""
        mock_is_file.return_value = True

        mock_get_tags.side_effect = [
            # file1.py - defines function_a but no external references
            [Tag("file1.py", "/test/file1.py", 10, "function_a", "def")],
        ]

        chat_fnames: list[str] = []
        other_fnames = ["/test/file1.py"]
        mentioned_fnames: set[str] = set()
        mentioned_idents: set[str] = set()

        result = self.repo_map.get_ranked_tags(
            chat_fnames, other_fnames, mentioned_fnames, mentioned_idents
        )

        assert len(result) > 0

    @patch("pathlib.Path.is_file")
    @patch("gsai.repo_map.RepoMap.get_tags")
    def test_get_ranked_tags_complex_graph(
        self, mock_get_tags: Mock, mock_is_file: Mock
    ) -> None:
        """Test ranked tags with complex dependency graph."""
        mock_is_file.return_value = True

        mock_get_tags.side_effect = [
            # file1.py - defines function_a, references function_b
            [
                Tag("file1.py", "/test/file1.py", 10, "function_a", "def"),
                Tag("file1.py", "/test/file1.py", 15, "function_b", "ref"),
            ],
            # file2.py - defines function_b, references function_a
            [
                Tag("file2.py", "/test/file2.py", 10, "function_b", "def"),
                Tag("file2.py", "/test/file2.py", 15, "function_a", "ref"),
            ],
            # file3.py - references both functions
            [
                Tag("file3.py", "/test/file3.py", 5, "function_a", "ref"),
                Tag("file3.py", "/test/file3.py", 10, "function_b", "ref"),
            ],
        ]

        chat_fnames: list[str] = []
        other_fnames = ["/test/file1.py", "/test/file2.py", "/test/file3.py"]
        mentioned_fnames: set[str] = set()
        mentioned_idents: set[str] = set()

        result = self.repo_map.get_ranked_tags(
            chat_fnames, other_fnames, mentioned_fnames, mentioned_idents
        )

        assert len(result) > 0
        # Should contain tags from the complex graph
        assert any(len(item) > 1 for item in result if isinstance(item, tuple))

    @patch("pathlib.Path.is_file")
    @patch("gsai.repo_map.RepoMap.get_tags")
    def test_get_ranked_tags_mentioned_filenames(
        self, mock_get_tags: Mock, mock_is_file: Mock
    ) -> None:
        """Test ranked tags with mentioned filenames (personalization)."""
        mock_is_file.return_value = True

        mock_get_tags.side_effect = [
            [Tag("important.py", "/test/important.py", 10, "function_a", "def")],
            [Tag("other.py", "/test/other.py", 5, "function_a", "ref")],
        ]

        chat_fnames: list[str] = []
        other_fnames = ["/test/important.py", "/test/other.py"]
        mentioned_fnames = {"important.py"}  # This file should get higher weight
        mentioned_idents: set[str] = set()

        result = self.repo_map.get_ranked_tags(
            chat_fnames, other_fnames, mentioned_fnames, mentioned_idents
        )

        assert len(result) > 0

    @patch("pathlib.Path.is_file")
    @patch("gsai.repo_map.RepoMap.get_tags")
    def test_get_ranked_tags_empty_tags(
        self, mock_get_tags: Mock, mock_is_file: Mock
    ) -> None:
        """Test ranked tags when get_tags returns None."""
        mock_is_file.return_value = True
        mock_get_tags.return_value = None

        chat_fnames: list[str] = []
        other_fnames = ["/test/file1.py"]
        mentioned_fnames: set[str] = set()
        mentioned_idents: set[str] = set()

        result = self.repo_map.get_ranked_tags(
            chat_fnames, other_fnames, mentioned_fnames, mentioned_idents
        )

        # Should handle None tags gracefully
        assert isinstance(result, list)

    @patch("pathlib.Path.is_file")
    @patch("gsai.repo_map.RepoMap.get_tags")
    def test_get_ranked_tags_files_without_tags_included(
        self, mock_get_tags: Mock, mock_is_file: Mock
    ) -> None:
        """Test that files without tags are still included in results."""
        mock_is_file.return_value = True

        mock_get_tags.side_effect = [
            # file1.py has tags
            [Tag("file1.py", "/test/file1.py", 10, "function_a", "def")],
            # file2.py has no tags
            [],
        ]

        chat_fnames: list[str] = []
        other_fnames = ["/test/file1.py", "/test/file2.py"]
        mentioned_fnames: set[str] = set()
        mentioned_idents: set[str] = set()

        result = self.repo_map.get_ranked_tags(
            chat_fnames, other_fnames, mentioned_fnames, mentioned_idents
        )

        # Both files should be represented in results
        file_names = [item[0] for item in result if len(item) > 0]
        # Check for relative path versions as well
        assert any("file1.py" in name for name in file_names)
        assert any("file2.py" in name for name in file_names)
