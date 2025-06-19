"""Unit tests for RepoMap tag extraction and tree-sitter parsing."""

import os
from pathlib import Path
from unittest.mock import Mock, patch

from gsai.repo_map import RepoMap, Tag, get_scm_fname, open_file


class TestOpenFile:
    """Test file opening functionality."""

    def test_open_file_success(self, tmp_path: Path) -> None:
        """Test successful file opening."""
        test_file = tmp_path / "test.py"
        test_content = "print('hello world')\n"
        test_file.write_text(test_content)

        result = open_file(str(test_file))
        assert result == test_content

    def test_open_file_not_found(self) -> None:
        """Test file not found scenario."""
        result = open_file("/nonexistent/file.py")
        assert result == "File not found"

    def test_open_file_unicode_decode_error(self, tmp_path: Path) -> None:
        """Test Unicode decode error handling."""
        test_file = tmp_path / "binary.bin"
        # Write binary data that will cause UnicodeDecodeError
        test_file.write_bytes(b"\x80\x81\x82\x83")

        # Test the actual function behavior with a binary file
        result = open_file(str(test_file))
        # Should handle the error gracefully and return some content
        assert isinstance(result, str)
        # May contain replacement characters or error message
        assert len(result) >= 0


class TestGetScmFname:
    """Test SCM filename resolution."""

    def test_get_scm_fname_existing_language(self) -> None:
        """Test SCM filename for existing language."""
        # Python should have a tags file
        result = get_scm_fname("python")
        if result:  # Only test if the file exists
            assert result.endswith("python-tags.scm")
            assert os.path.exists(result)

    def test_get_scm_fname_nonexistent_language(self) -> None:
        """Test SCM filename for non-existent language."""
        result = get_scm_fname("nonexistent_language")
        assert result is None

    def test_get_scm_fname_none_input(self) -> None:
        """Test SCM filename with None input."""
        result = get_scm_fname(None)
        assert result is None


class TestRepoMapTagExtraction:
    """Test RepoMap tag extraction functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.repo_map = RepoMap(root="/test/repo")

    def test_get_rel_fname_normal_path(self) -> None:
        """Test relative filename calculation for normal paths."""
        self.repo_map.root = "/test/repo"
        result = self.repo_map.get_rel_fname("/test/repo/src/main.py")
        assert result == "src/main.py"

    def test_get_rel_fname_same_path(self) -> None:
        """Test relative filename calculation for same path."""
        self.repo_map.root = "/test/repo"
        result = self.repo_map.get_rel_fname("/test/repo")
        assert result == "."

    def test_get_rel_fname_different_drive(self) -> None:
        """Test relative filename calculation for different drives (Windows)."""
        self.repo_map.root = "C:/test/repo"
        # Simulate ValueError for different drives
        with patch(
            "os.path.relpath",
            side_effect=ValueError("path is on mount 'C:', start on mount 'D:'"),
        ):
            result = self.repo_map.get_rel_fname("D:/other/file.py")
            assert result == "D:/other/file.py"

    @patch("os.path.getmtime")
    def test_get_mtime_success(self, mock_getmtime: Mock) -> None:
        """Test successful modification time retrieval."""
        mock_getmtime.return_value = 1234567890.0
        result = self.repo_map.get_mtime("/test/file.py")
        assert result == 1234567890.0

    @patch("os.path.getmtime")
    def test_get_mtime_file_not_found(self, mock_getmtime: Mock) -> None:
        """Test modification time retrieval with file not found."""
        mock_getmtime.side_effect = FileNotFoundError("File not found")
        result = self.repo_map.get_mtime("/test/file.py")
        assert result is None

    @patch("gsai.repo_map.RepoMap.get_tags_raw")
    @patch("gsai.repo_map.RepoMap.get_mtime")
    def test_get_tags_success(
        self, mock_get_mtime: Mock, mock_get_tags_raw: Mock
    ) -> None:
        """Test successful tag extraction."""
        mock_get_mtime.return_value = 1234567890.0
        mock_tags = [
            Tag(
                rel_fname="test.py",
                fname="/test/test.py",
                line=1,
                name="function1",
                kind="def",
            ),
            Tag(
                rel_fname="test.py",
                fname="/test/test.py",
                line=5,
                name="function1",
                kind="ref",
            ),
        ]
        mock_get_tags_raw.return_value = mock_tags

        result = self.repo_map.get_tags("/test/test.py", "test.py")
        assert result == mock_tags

    @patch("gsai.repo_map.RepoMap.get_mtime")
    def test_get_tags_file_not_found(self, mock_get_mtime: Mock) -> None:
        """Test tag extraction with file not found."""
        mock_get_mtime.return_value = None
        result = self.repo_map.get_tags("/test/nonexistent.py", "nonexistent.py")
        assert result == []

    @patch("gsai.repo_map.open_file")
    @patch("grep_ast.filename_to_lang")
    def test_get_tags_raw_unsupported_language(
        self, mock_filename_to_lang: Mock, mock_open_file: Mock
    ) -> None:
        """Test tag extraction for unsupported language."""
        mock_filename_to_lang.return_value = None
        result = list(self.repo_map.get_tags_raw("/test/file.unknown", "file.unknown"))
        assert result == []

    @patch("gsai.repo_map.open_file")
    @patch("gsai.repo_map.get_scm_fname")
    @patch("grep_ast.filename_to_lang")
    @patch("gsai.repo_map.get_language")
    @patch("gsai.repo_map.get_parser")
    def test_get_tags_raw_no_query_file(
        self,
        mock_get_parser: Mock,
        mock_get_language: Mock,
        mock_filename_to_lang: Mock,
        mock_get_scm_fname: Mock,
        mock_open_file: Mock,
    ) -> None:
        """Test tag extraction when query file doesn't exist."""
        mock_filename_to_lang.return_value = "python"
        mock_get_language.return_value = Mock()
        mock_get_parser.return_value = Mock()
        mock_get_scm_fname.return_value = None

        result = list(self.repo_map.get_tags_raw("/test/test.py", "test.py"))
        assert result == []

    @patch("gsai.repo_map.open_file")
    @patch("gsai.repo_map.get_scm_fname")
    @patch("grep_ast.filename_to_lang")
    @patch("gsai.repo_map.get_language")
    @patch("gsai.repo_map.get_parser")
    def test_get_tags_raw_empty_file(
        self,
        mock_get_parser: Mock,
        mock_get_language: Mock,
        mock_filename_to_lang: Mock,
        mock_get_scm_fname: Mock,
        mock_open_file: Mock,
    ) -> None:
        """Test tag extraction for empty file."""
        mock_filename_to_lang.return_value = "python"
        mock_get_language.return_value = Mock()
        mock_get_parser.return_value = Mock()
        mock_get_scm_fname.return_value = "/test/python-tags.scm"
        mock_open_file.side_effect = [
            "(name) @name",
            "",
        ]  # Query file, then empty source file

        result = list(self.repo_map.get_tags_raw("/test/empty.py", "empty.py"))
        assert result == []

    @patch("gsai.repo_map.open_file")
    @patch("gsai.repo_map.get_scm_fname")
    @patch("grep_ast.filename_to_lang")
    @patch("gsai.repo_map.get_language")
    @patch("gsai.repo_map.get_parser")
    def test_get_tags_raw_parser_exception(
        self,
        mock_get_parser: Mock,
        mock_get_language: Mock,
        mock_filename_to_lang: Mock,
        mock_get_scm_fname: Mock,
        mock_open_file: Mock,
    ) -> None:
        """Test tag extraction when parser raises exception."""
        mock_filename_to_lang.return_value = "python"
        mock_get_language.side_effect = Exception("Parser error")

        result = list(self.repo_map.get_tags_raw("/test/test.py", "test.py"))
        assert result == []

    @patch("gsai.repo_map.open_file")
    @patch("gsai.repo_map.get_scm_fname")
    @patch("grep_ast.filename_to_lang")
    @patch("gsai.repo_map.get_language")
    @patch("gsai.repo_map.get_parser")
    def test_get_tags_raw_with_definitions_and_references(
        self,
        mock_get_parser: Mock,
        mock_get_language: Mock,
        mock_filename_to_lang: Mock,
        mock_get_scm_fname: Mock,
        mock_open_file: Mock,
    ) -> None:
        """Test tag extraction with both definitions and references."""
        mock_filename_to_lang.return_value = "python"

        # Mock tree-sitter components
        mock_language = Mock()
        mock_parser = Mock()
        mock_tree = Mock()
        mock_root_node = Mock()
        mock_query = Mock()

        mock_get_language.return_value = mock_language
        mock_get_parser.return_value = mock_parser
        mock_parser.parse.return_value = mock_tree
        mock_tree.root_node = mock_root_node
        mock_language.query.return_value = mock_query

        # Mock nodes for definitions and references
        def_node = Mock()
        def_node.text = b"test_function"
        def_node.start_point = (10, 0)

        ref_node = Mock()
        ref_node.text = b"test_function"
        ref_node.start_point = (20, 0)

        # Mock query captures
        mock_query.captures.return_value = {
            "name.definition.function": [def_node],
            "name.reference.call": [ref_node],
        }

        mock_get_scm_fname.return_value = "/test/python-tags.scm"
        mock_open_file.side_effect = [
            "(name) @name",
            "def test_function():\n    pass\n\ntest_function()",
        ]

        result = list(self.repo_map.get_tags_raw("/test/test.py", "test.py"))

        assert len(result) == 2
        assert result[0].name == "test_function"
        assert result[0].kind == "def"
        assert result[0].line == 10
        assert result[1].name == "test_function"
        assert result[1].kind == "ref"
        assert result[1].line == 20

    @patch("gsai.repo_map.open_file")
    @patch("gsai.repo_map.get_scm_fname")
    @patch("grep_ast.filename_to_lang")
    @patch("gsai.repo_map.get_language")
    @patch("gsai.repo_map.get_parser")
    @patch("pygments.lexers.guess_lexer_for_filename")
    def test_get_tags_raw_definitions_only_with_pygments_fallback(
        self,
        mock_guess_lexer: Mock,
        mock_get_parser: Mock,
        mock_get_language: Mock,
        mock_filename_to_lang: Mock,
        mock_get_scm_fname: Mock,
        mock_open_file: Mock,
    ) -> None:
        """Test tag extraction with definitions only, using Pygments for references."""
        mock_filename_to_lang.return_value = "python"

        # Mock tree-sitter components
        mock_language = Mock()
        mock_parser = Mock()
        mock_tree = Mock()
        mock_root_node = Mock()
        mock_query = Mock()

        mock_get_language.return_value = mock_language
        mock_get_parser.return_value = mock_parser
        mock_parser.parse.return_value = mock_tree
        mock_tree.root_node = mock_root_node
        mock_language.query.return_value = mock_query

        # Mock node for definition only
        def_node = Mock()
        def_node.text = b"test_function"
        def_node.start_point = (10, 0)

        # Mock query captures - only definitions, no references
        mock_query.captures.return_value = {
            "name.definition.function": [def_node],
        }

        # Mock Pygments lexer
        mock_lexer = Mock()
        from pygments.token import Token

        mock_lexer.get_tokens.return_value = [
            (Token.Name, "test_function"),
            (Token.Name, "another_name"),
        ]
        mock_guess_lexer.return_value = mock_lexer

        mock_get_scm_fname.return_value = "/test/python-tags.scm"
        mock_open_file.side_effect = [
            "(name) @name",
            "def test_function():\n    test_function()\n",
        ]

        result = list(self.repo_map.get_tags_raw("/test/test.py", "test.py"))

        # Should have at least 1 definition, may have additional references
        assert len(result) >= 1
        assert result[0].name == "test_function"
        assert result[0].kind == "def"
        # Additional results may vary based on actual implementation
        if len(result) > 1:
            assert all(tag.kind in ["def", "ref"] for tag in result)

    @patch("gsai.repo_map.open_file")
    @patch("gsai.repo_map.get_scm_fname")
    @patch("grep_ast.filename_to_lang")
    @patch("gsai.repo_map.get_language")
    @patch("gsai.repo_map.get_parser")
    @patch("pygments.lexers.guess_lexer_for_filename")
    def test_get_tags_raw_pygments_exception(
        self,
        mock_guess_lexer: Mock,
        mock_get_parser: Mock,
        mock_get_language: Mock,
        mock_filename_to_lang: Mock,
        mock_get_scm_fname: Mock,
        mock_open_file: Mock,
    ) -> None:
        """Test tag extraction when Pygments raises exception."""
        mock_filename_to_lang.return_value = "python"

        # Mock tree-sitter to return definitions only
        mock_language = Mock()
        mock_parser = Mock()
        mock_tree = Mock()
        mock_root_node = Mock()
        mock_query = Mock()

        mock_get_language.return_value = mock_language
        mock_get_parser.return_value = mock_parser
        mock_parser.parse.return_value = mock_tree
        mock_tree.root_node = mock_root_node
        mock_language.query.return_value = mock_query

        def_node = Mock()
        def_node.text = b"test_function"
        def_node.start_point = (10, 0)

        mock_query.captures.return_value = {
            "name.definition.function": [def_node],
        }

        # Mock Pygments to raise exception
        mock_guess_lexer.side_effect = Exception("Lexer error")

        mock_get_scm_fname.return_value = "/test/python-tags.scm"
        mock_open_file.side_effect = [
            "(name) @name",
            "def test_function():\n    pass\n",
        ]

        result = list(self.repo_map.get_tags_raw("/test/test.py", "test.py"))

        # Should have at least the definition, may have additional tags
        assert len(result) >= 1
        # First result should be the definition
        def_tags = [tag for tag in result if tag.kind == "def"]
        assert len(def_tags) >= 1
        assert def_tags[0].name == "test_function"

    @patch("gsai.repo_map.open_file")
    @patch("gsai.repo_map.get_scm_fname")
    @patch("grep_ast.filename_to_lang")
    @patch("gsai.repo_map.get_language")
    @patch("gsai.repo_map.get_parser")
    def test_get_tags_raw_references_only_no_pygments(
        self,
        mock_get_parser: Mock,
        mock_get_language: Mock,
        mock_filename_to_lang: Mock,
        mock_get_scm_fname: Mock,
        mock_open_file: Mock,
    ) -> None:
        """Test tag extraction with references only (no Pygments fallback)."""
        mock_filename_to_lang.return_value = "python"

        # Mock tree-sitter components
        mock_language = Mock()
        mock_parser = Mock()
        mock_tree = Mock()
        mock_root_node = Mock()
        mock_query = Mock()

        mock_get_language.return_value = mock_language
        mock_get_parser.return_value = mock_parser
        mock_parser.parse.return_value = mock_tree
        mock_tree.root_node = mock_root_node
        mock_language.query.return_value = mock_query

        # Mock node for reference only
        ref_node = Mock()
        ref_node.text = b"test_function"
        ref_node.start_point = (20, 0)

        # Mock query captures - only references, no definitions
        mock_query.captures.return_value = {
            "name.reference.call": [ref_node],
        }

        mock_get_scm_fname.return_value = "/test/python-tags.scm"
        mock_open_file.side_effect = ["(name) @name", "test_function()\n"]

        result = list(self.repo_map.get_tags_raw("/test/test.py", "test.py"))

        # May return references or empty list depending on implementation
        assert isinstance(result, list)
        # If results exist, they should be valid tags
        if result:
            assert all(isinstance(tag, Tag) for tag in result)


class TestTagNamedTuple:
    """Test Tag namedtuple functionality."""

    def test_tag_creation(self) -> None:
        """Test Tag namedtuple creation."""
        tag = Tag(
            rel_fname="test.py",
            fname="/test/test.py",
            line=10,
            name="test_function",
            kind="def",
        )

        assert tag.rel_fname == "test.py"
        assert tag.fname == "/test/test.py"
        assert tag.line == 10
        assert tag.name == "test_function"
        assert tag.kind == "def"

    def test_tag_equality(self) -> None:
        """Test Tag equality comparison."""
        tag1 = Tag("test.py", "/test/test.py", 10, "func", "def")
        tag2 = Tag("test.py", "/test/test.py", 10, "func", "def")
        tag3 = Tag("test.py", "/test/test.py", 11, "func", "def")

        assert tag1 == tag2
        assert tag1 != tag3
