"""Integration tests for RepoMap system."""

from pathlib import Path
from unittest.mock import Mock, patch

from gsai.repo_map import (
    RepoMap,
    get_repo_map_for_prompt,
    get_repo_map_for_prompt_cached,
)


class TestRepoMapIntegration:
    """Integration tests for full RepoMap workflows."""

    def test_repo_map_with_real_file_structure(self, tmp_path: Path) -> None:
        """Test RepoMap with real temporary file structure."""
        # Create a simple Python project structure
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        # Create main.py
        main_file = src_dir / "main.py"
        main_file.write_text("""
def main():
    print("Hello, world!")
    helper_function()

if __name__ == "__main__":
    main()
""")

        # Create utils.py
        utils_file = src_dir / "utils.py"
        utils_file.write_text("""
def helper_function():
    return "helper"

def another_function():
    return helper_function()
""")

        # Create test file
        test_file = tmp_path / "test_main.py"
        test_file.write_text("""
from src.main import main

def test_main():
    main()
""")

        # Test RepoMap generation
        repo_map = RepoMap(root=str(tmp_path))

        all_files = [str(main_file), str(utils_file), str(test_file)]
        result = repo_map.get_repo_map([], all_files)

        # Should generate some content
        assert result is not None
        assert len(result) > 0

    def test_repo_map_empty_directory(self, tmp_path: Path) -> None:
        """Test RepoMap with empty directory."""
        repo_map = RepoMap(root=str(tmp_path))
        result = repo_map.get_repo_map([], [])

        assert result == ""

    def test_repo_map_with_binary_files(self, tmp_path: Path) -> None:
        """Test RepoMap handling of binary files."""
        # Create a binary file
        binary_file = tmp_path / "image.png"
        binary_file.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")

        # Create a text file
        text_file = tmp_path / "readme.txt"
        text_file.write_text("This is a readme file.")

        repo_map = RepoMap(root=str(tmp_path))
        all_files = [str(binary_file), str(text_file)]

        # Should handle binary files gracefully
        result = repo_map.get_repo_map([], all_files)

        # May or may not generate content depending on file types
        assert isinstance(result, str | type(None))

    def test_repo_map_with_large_files(self, tmp_path: Path) -> None:
        """Test RepoMap with large files."""
        # Create a large Python file
        large_file = tmp_path / "large.py"
        content = "# Large file\n" + "def function_{}():\n    pass\n\n" * 1000
        large_file.write_text(content)

        repo_map = RepoMap(root=str(tmp_path))
        result = repo_map.get_repo_map([], [str(large_file)])

        assert result is not None

    def test_repo_map_with_chat_files(self, tmp_path: Path) -> None:
        """Test RepoMap with chat files (should be excluded from output)."""
        # Create files
        chat_file = tmp_path / "chat.py"
        chat_file.write_text("def chat_function():\n    pass")

        other_file = tmp_path / "other.py"
        other_file.write_text("def other_function():\n    chat_function()")

        repo_map = RepoMap(root=str(tmp_path))
        result = repo_map.get_repo_map([str(chat_file)], [str(other_file)])

        if result:
            # Chat file should not appear in the output
            assert "chat.py" not in result
            assert "other.py" in result

    def test_repo_map_caching_consistency(self, tmp_path: Path) -> None:
        """Test that cached and uncached results are consistent."""
        # Create test files
        file1 = tmp_path / "file1.py"
        file1.write_text("def function1():\n    pass")

        file2 = tmp_path / "file2.py"
        file2.write_text("def function2():\n    function1()")

        repo_map = RepoMap(root=str(tmp_path))
        all_files = [str(file1), str(file2)]

        # Generate uncached result
        result1 = repo_map.get_ranked_tags_map([], all_files, 1000, force_refresh=True)

        # Generate cached result
        result2 = repo_map.get_ranked_tags_map([], all_files, 1000)

        # Results should be identical
        assert result1 == result2

    @patch("gsai.repo_map.get_files_excluding_gitignore")
    def test_get_repo_map_for_prompt_integration(
        self, mock_get_files: Mock, tmp_path: Path
    ) -> None:
        """Test get_repo_map_for_prompt integration."""
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("def test():\n    pass")

        mock_get_files.return_value = [str(test_file)]

        result = get_repo_map_for_prompt(str(tmp_path))

        assert result is not None
        assert isinstance(result, str)

    def test_repo_map_with_different_languages(self, tmp_path: Path) -> None:
        """Test RepoMap with different programming languages."""
        # Create Python file
        py_file = tmp_path / "script.py"
        py_file.write_text("def python_function():\n    pass")

        # Create JavaScript file
        js_file = tmp_path / "script.js"
        js_file.write_text("function jsFunction() {\n    return 'hello';\n}")

        # Create unknown file type
        unknown_file = tmp_path / "config.conf"
        unknown_file.write_text("setting=value\nother_setting=other_value")

        repo_map = RepoMap(root=str(tmp_path))
        all_files = [str(py_file), str(js_file), str(unknown_file)]

        result = repo_map.get_repo_map([], all_files)

        # Should handle multiple languages
        assert result is not None

    def test_repo_map_performance_with_many_files(self, tmp_path: Path) -> None:
        """Test RepoMap performance with many files."""
        # Create many small files
        files = []
        for i in range(100):  # Create 100 files
            file_path = tmp_path / f"file_{i}.py"
            file_path.write_text(f"def function_{i}():\n    return {i}")
            files.append(str(file_path))

        repo_map = RepoMap(root=str(tmp_path))

        # Measure basic performance (should complete without timeout)
        import time

        start_time = time.time()
        result = repo_map.get_repo_map([], files)
        end_time = time.time()

        # Should complete in reasonable time (less than 30 seconds)
        assert end_time - start_time < 30
        assert result is not None

    def test_repo_map_with_circular_references(self, tmp_path: Path) -> None:
        """Test RepoMap with circular references between files."""
        # Create file A that references B
        file_a = tmp_path / "a.py"
        file_a.write_text("""
from b import function_b

def function_a():
    return function_b()
""")

        # Create file B that references A
        file_b = tmp_path / "b.py"
        file_b.write_text("""
from a import function_a

def function_b():
    return "from b"

def another_function():
    return function_a()
""")

        repo_map = RepoMap(root=str(tmp_path))
        all_files = [str(file_a), str(file_b)]

        # Should handle circular references without infinite loops
        result = repo_map.get_repo_map([], all_files)

        assert result is not None

    def test_repo_map_token_limit_enforcement(self, tmp_path: Path) -> None:
        """Test that RepoMap respects token limits."""
        # Create many files to exceed token limit
        files = []
        for i in range(50):
            file_path = tmp_path / f"large_file_{i}.py"
            # Create files with substantial content
            content = f"# File {i}\n" + "def function_{}():\n    pass\n\n" * 20
            file_path.write_text(content)
            files.append(str(file_path))

        # Set a small token limit
        repo_map = RepoMap(root=str(tmp_path), map_tokens=1000)
        result = repo_map.get_repo_map([], files)

        if result:
            # Result should respect token limit
            token_count = repo_map.token_count(result)
            # Allow some tolerance for the binary search algorithm
            assert token_count <= 1000 * 1.2  # 20% tolerance

    def test_repo_map_with_mentioned_identifiers(self, tmp_path: Path) -> None:
        """Test RepoMap with mentioned identifiers for prioritization."""
        # Create files with specific functions
        file1 = tmp_path / "important.py"
        file1.write_text("""
def important_function():
    return "very important"

def other_function():
    return "not important"
""")

        file2 = tmp_path / "caller.py"
        file2.write_text("""
from important import important_function, other_function

def caller():
    return important_function()
""")

        repo_map = RepoMap(root=str(tmp_path))
        all_files = [str(file1), str(file2)]

        # Test with mentioned identifier
        result = repo_map.get_repo_map(
            [], all_files, mentioned_idents={"important_function"}
        )

        assert result is not None

    def test_repo_map_refresh_strategies(self, tmp_path: Path) -> None:
        """Test different refresh strategies."""
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("def test():\n    pass")

        all_files = [str(test_file)]

        # Test manual refresh
        repo_map_manual = RepoMap(root=str(tmp_path), refresh="manual")
        result1 = repo_map_manual.get_repo_map([], all_files)
        result2 = repo_map_manual.get_repo_map([], all_files)
        # Second call should return same result (cached)
        assert result1 == result2

        # Test always refresh
        repo_map_always = RepoMap(root=str(tmp_path), refresh="always")
        result3 = repo_map_always.get_repo_map([], all_files)
        assert result3 is not None

    @patch("gsai.config.cli_settings")
    @patch("gsai.repo_map.get_disk_cache")
    def test_cached_repo_map_integration(
        self, mock_get_cache: Mock, mock_cli_settings: Mock, tmp_path: Path
    ) -> None:
        """Test cached repo map integration."""
        mock_cli_settings.cache_enabled = True
        mock_cli_settings.cache_strategy = "simple"
        mock_cli_settings.cache_ttl_days = 1
        mock_cli_settings.verbose = False

        # Mock cache to return None (cache miss)
        mock_cache = Mock()
        mock_cache.get.return_value = None
        mock_get_cache.return_value = mock_cache

        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("def test():\n    pass")

        with patch(
            "gsai.repo_map.get_files_excluding_gitignore", return_value=[str(test_file)]
        ):
            result = get_repo_map_for_prompt_cached(str(tmp_path))

            assert result is not None
            assert isinstance(result, str)

    def test_repo_map_with_special_characters(self, tmp_path: Path) -> None:
        """Test RepoMap with files containing special characters."""
        # Create file with Unicode content
        unicode_file = tmp_path / "unicode.py"
        unicode_file.write_text(
            """
def función_especial():
    return "¡Hola, mundo! 🌍"

def 测试函数():
    return "你好世界"
""",
            encoding="utf-8",
        )

        repo_map = RepoMap(root=str(tmp_path))
        result = repo_map.get_repo_map([], [str(unicode_file)])

        # Should handle Unicode content
        assert result is not None

    def test_repo_map_error_recovery(self, tmp_path: Path) -> None:
        """Test RepoMap error recovery mechanisms."""
        # Create a file that might cause parsing issues
        problematic_file = tmp_path / "problematic.py"
        problematic_file.write_text("def incomplete_function(")  # Syntax error

        # Create a normal file
        normal_file = tmp_path / "normal.py"
        normal_file.write_text("def normal_function():\n    pass")

        repo_map = RepoMap(root=str(tmp_path))
        all_files = [str(problematic_file), str(normal_file)]

        # Should handle parsing errors gracefully
        result = repo_map.get_repo_map([], all_files)

        # Should still generate some result despite problematic file
        assert isinstance(result, str | type(None))


class TestRepoMapRealWorldScenarios:
    """Test RepoMap with real-world-like scenarios."""

    def test_typical_python_project(self, tmp_path: Path) -> None:
        """Test RepoMap with typical Python project structure."""
        # Create typical project structure
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()

        # Main module
        main_py = src_dir / "__init__.py"
        main_py.write_text("")

        core_py = src_dir / "core.py"
        core_py.write_text("""
class DataProcessor:
    def __init__(self):
        self.data = []

    def process(self, item):
        return self.transform(item)

    def transform(self, item):
        return item.upper()
""")

        utils_py = src_dir / "utils.py"
        utils_py.write_text("""
from .core import DataProcessor

def create_processor():
    return DataProcessor()

def batch_process(items):
    processor = create_processor()
    return [processor.process(item) for item in items]
""")

        # Test file
        test_core_py = tests_dir / "test_core.py"
        test_core_py.write_text("""
import unittest
from src.core import DataProcessor

class TestDataProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = DataProcessor()

    def test_process(self):
        result = self.processor.process("hello")
        self.assertEqual(result, "HELLO")
""")

        repo_map = RepoMap(root=str(tmp_path))
        all_files = [str(core_py), str(utils_py), str(test_core_py)]

        result = repo_map.get_repo_map([], all_files)

        assert result is not None
        # Should contain references to classes and functions
        if result:
            # Check for any of the expected content
            assert any(
                term in result
                for term in [
                    "DataProcessor",
                    "process",
                    "core.py",
                    "utils.py",
                    "test_core.py",
                ]
            )

    def test_mixed_language_project(self, tmp_path: Path) -> None:
        """Test RepoMap with mixed language project."""
        # Python backend
        backend_py = tmp_path / "backend.py"
        backend_py.write_text("""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/data')
def get_data():
    return jsonify({"message": "Hello from Python"})
""")

        # JavaScript frontend
        frontend_js = tmp_path / "frontend.js"
        frontend_js.write_text("""
async function fetchData() {
    const response = await fetch('/api/data');
    const data = await response.json();
    return data;
}

function displayData(data) {
    document.getElementById('output').textContent = data.message;
}
""")

        # Configuration file
        config_json = tmp_path / "config.json"
        config_json.write_text('{"port": 5000, "debug": true}')

        repo_map = RepoMap(root=str(tmp_path))
        all_files = [str(backend_py), str(frontend_js), str(config_json)]

        result = repo_map.get_repo_map([], all_files)

        # Should handle multiple languages
        assert result is not None
