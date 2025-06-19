"""Shared pytest fixtures for the GitStart AI CLI test suite."""

import os
import shutil
import subprocess
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from gsai.repo_map import Tag


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    tmp_dir = Path(tempfile.mkdtemp())
    try:
        yield tmp_dir
    finally:
        shutil.rmtree(tmp_dir)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment() -> Generator[None, None, None]:
    """Set up test environment variables before any tests run."""
    # Store original values
    original_anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    original_openai_key = os.environ.get("OPENAI_API_KEY")

    # Set dummy keys for tests
    os.environ["ANTHROPIC_API_KEY"] = "dummy-anthropic-key-for-tests"
    os.environ["OPENAI_API_KEY"] = "dummy-openai-key-for-tests"

    try:
        yield
    finally:
        # Restore original values
        if original_anthropic_key is not None:
            os.environ["ANTHROPIC_API_KEY"] = original_anthropic_key
        else:
            os.environ.pop("ANTHROPIC_API_KEY", None)

        if original_openai_key is not None:
            os.environ["OPENAI_API_KEY"] = original_openai_key
        else:
            os.environ.pop("OPENAI_API_KEY", None)


@pytest.fixture
def cli_runner() -> CliRunner:
    """Set up a Typer CLI runner for testing commands."""
    return CliRunner()


# RepoMap test fixtures


@pytest.fixture
def sample_python_file(tmp_path: Path) -> Path:
    """Create a sample Python file for testing."""
    file_path = tmp_path / "sample.py"
    content = '''"""Sample Python module for testing."""

def main_function():
    """Main function that calls helper."""
    result = helper_function("test")
    return process_result(result)

def helper_function(arg):
    """Helper function."""
    return f"processed: {arg}"

def process_result(data):
    """Process the result."""
    return data.upper()

class SampleClass:
    """Sample class for testing."""

    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

if __name__ == "__main__":
    main_function()
'''
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_javascript_file(tmp_path: Path) -> Path:
    """Create a sample JavaScript file for testing."""
    file_path = tmp_path / "sample.js"
    content = """/**
 * Sample JavaScript module for testing.
 */

function mainFunction() {
    const result = helperFunction("test");
    return processResult(result);
}

function helperFunction(arg) {
    return `processed: ${arg}`;
}

function processResult(data) {
    return data.toUpperCase();
}

class SampleClass {
    constructor(name) {
        this.name = name;
    }

    getName() {
        return this.name;
    }

    setName(name) {
        this.name = name;
    }
}

// Export for testing
if (typeof module !== 'undefined') {
    module.exports = { mainFunction, SampleClass };
}
"""
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_tag_data() -> list[Tag]:
    """Create sample tag data for testing."""
    return [
        Tag("file1.py", "/test/file1.py", 10, "main_function", "def"),
        Tag("file1.py", "/test/file1.py", 15, "helper_function", "def"),
        Tag("file1.py", "/test/file1.py", 20, "SampleClass", "def"),
        Tag("file2.py", "/test/file2.py", 5, "main_function", "ref"),
        Tag("file2.py", "/test/file2.py", 8, "helper_function", "ref"),
        Tag("file2.py", "/test/file2.py", 12, "SampleClass", "ref"),
    ]


@pytest.fixture
def test_repository(tmp_path: Path) -> Path:
    """Create a test repository with multiple files."""
    # Create directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()

    # Create main module
    main_py = src_dir / "main.py"
    main_py.write_text('''
from .utils import process_data
from .models import DataModel

def main():
    """Main entry point."""
    model = DataModel("test")
    data = model.get_data()
    return process_data(data)

if __name__ == "__main__":
    main()
''')

    # Create utils module
    utils_py = src_dir / "utils.py"
    utils_py.write_text('''
def process_data(data):
    """Process data with validation."""
    if not data:
        raise ValueError("Data cannot be empty")
    return data.upper()

def validate_input(input_data):
    """Validate input data."""
    return isinstance(input_data, str) and len(input_data) > 0
''')

    # Create models module
    models_py = src_dir / "models.py"
    models_py.write_text('''
class DataModel:
    """Data model class."""

    def __init__(self, name):
        self.name = name
        self._data = None

    def get_data(self):
        """Get data from model."""
        if self._data is None:
            self._data = f"data for {self.name}"
        return self._data

    def set_data(self, data):
        """Set data in model."""
        self._data = data
''')

    # Create test file
    test_main_py = tests_dir / "test_main.py"
    test_main_py.write_text('''
import unittest
from src.main import main
from src.models import DataModel

class TestMain(unittest.TestCase):
    def test_main(self):
        """Test main function."""
        result = main()
        self.assertIsInstance(result, str)

    def test_data_model(self):
        """Test data model."""
        model = DataModel("test")
        data = model.get_data()
        self.assertEqual(data, "data for test")
''')

    # Create README
    readme = tmp_path / "README.md"
    readme.write_text("""# Test Repository

This is a test repository for RepoMap testing.

## Structure

- `src/` - Main source code
- `tests/` - Test files
""")

    return tmp_path


@pytest.fixture
def git_repository(tmp_path: Path) -> Path:
    """Create a git repository for testing git-related functionality."""
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"], cwd=tmp_path, check=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True
    )

    # Create initial file
    test_file = tmp_path / "initial.py"
    test_file.write_text("def initial_function():\n    pass\n")

    # Add and commit
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=tmp_path, check=True)

    return tmp_path


@pytest.fixture
def large_repository(tmp_path: Path) -> Path:
    """Create a large repository for performance testing."""
    # Create many files
    for i in range(100):
        file_path = tmp_path / f"file_{i:03d}.py"
        content = f'''
def function_{i}():
    """Function number {i}."""
    return {i}

def helper_{i}():
    """Helper function {i}."""
    return function_{i}() * 2

class Class_{i}:
    """Class number {i}."""

    def __init__(self):
        self.value = {i}

    def get_value(self):
        return self.value
'''
        file_path.write_text(content)

    return tmp_path


@pytest.fixture
def mixed_language_repository(tmp_path: Path) -> Path:
    """Create a repository with multiple programming languages."""
    # Python file
    py_file = tmp_path / "script.py"
    py_file.write_text("""
def python_function():
    return "Hello from Python"

class PythonClass:
    def method(self):
        return python_function()
""")

    # JavaScript file
    js_file = tmp_path / "script.js"
    js_file.write_text("""
function jsFunction() {
    return "Hello from JavaScript";
}

class JSClass {
    method() {
        return jsFunction();
    }
}
""")

    # TypeScript file
    ts_file = tmp_path / "script.ts"
    ts_file.write_text("""
function tsFunction(): string {
    return "Hello from TypeScript";
}

class TSClass {
    method(): string {
        return tsFunction();
    }
}
""")

    # Go file
    go_file = tmp_path / "script.go"
    go_file.write_text("""
package main

import "fmt"

func goFunction() string {
    return "Hello from Go"
}

type GoStruct struct {
    value string
}

func (g *GoStruct) Method() string {
    return goFunction()
}

func main() {
    fmt.Println(goFunction())
}
""")

    # Configuration files
    json_file = tmp_path / "config.json"
    json_file.write_text('{"setting": "value", "debug": true}')

    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text("""
database:
  host: localhost
  port: 5432
  name: testdb
""")

    return tmp_path


@pytest.fixture
def mock_tag_data_complex() -> dict[str, Any]:
    """Create complex mock tag data for testing ranking algorithms."""
    return {
        "defines": {
            "important_function": {"file1.py", "file2.py"},
            "helper_function": {"file1.py"},
            "utility_function": {"file3.py"},
            "_private_function": {"file2.py"},
            "commonName": {
                "file1.py",
                "file2.py",
                "file3.py",
                "file4.py",
                "file5.py",
                "file6.py",
            },
        },
        "references": {
            "important_function": ["file3.py", "file4.py", "file5.py"],
            "helper_function": ["file1.py", "file3.py"],
            "utility_function": ["file1.py", "file2.py"],
            "_private_function": ["file2.py"],
            "commonName": ["file1.py"] * 10,  # High frequency reference
        },
        "definitions": {
            ("file1.py", "important_function"): [
                Tag("file1.py", "/test/file1.py", 10, "important_function", "def")
            ],
            ("file1.py", "helper_function"): [
                Tag("file1.py", "/test/file1.py", 20, "helper_function", "def")
            ],
            ("file2.py", "important_function"): [
                Tag("file2.py", "/test/file2.py", 15, "important_function", "def")
            ],
            ("file2.py", "_private_function"): [
                Tag("file2.py", "/test/file2.py", 25, "_private_function", "def")
            ],
            ("file3.py", "utility_function"): [
                Tag("file3.py", "/test/file3.py", 5, "utility_function", "def")
            ],
        },
    }
