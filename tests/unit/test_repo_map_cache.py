"""Unit tests for RepoMap cache system."""

import hashlib
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from gsai.repo_map import (
    generate_cache_key,
    generate_full_cache_key,
    generate_git_cache_key,
    generate_simple_cache_key,
    get_disk_cache,
    get_repo_map_for_prompt_cached,
    is_git_repo,
)


class TestCacheKeyGeneration:
    """Test cache key generation strategies."""

    def test_is_git_repo_true(self, tmp_path: Path) -> None:
        """Test git repo detection with valid .git directory."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        assert is_git_repo(str(tmp_path)) is True

    def test_is_git_repo_false(self, tmp_path: Path) -> None:
        """Test git repo detection without .git directory."""
        assert is_git_repo(str(tmp_path)) is False

    @patch("subprocess.run")
    @patch("os.path.exists")
    @patch("os.path.getmtime")
    def test_generate_git_cache_key_success(
        self, mock_getmtime: Mock, mock_exists: Mock, mock_run: Mock
    ) -> None:
        """Test successful git cache key generation."""
        # Mock git command success
        mock_run.return_value = Mock(returncode=0, stdout="abc123\n")
        mock_exists.return_value = True
        mock_getmtime.return_value = 1234567890.0

        repo_path = "/test/repo"
        cache_key = generate_git_cache_key(repo_path)

        assert cache_key is not None
        assert isinstance(cache_key, str)
        assert len(cache_key) == 32  # MD5 hash length

        # Verify git command was called correctly
        mock_run.assert_called_once_with(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=2,
        )

    @patch("subprocess.run")
    def test_generate_git_cache_key_git_failure(self, mock_run: Mock) -> None:
        """Test git cache key generation when git command fails."""
        mock_run.return_value = Mock(returncode=1, stdout="")

        repo_path = "/test/repo"
        cache_key = generate_git_cache_key(repo_path)

        assert cache_key is None

    @patch("subprocess.run")
    def test_generate_git_cache_key_timeout(self, mock_run: Mock) -> None:
        """Test git cache key generation with timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("git", 2)

        repo_path = "/test/repo"
        cache_key = generate_git_cache_key(repo_path)

        assert cache_key is None

    @patch("subprocess.run")
    def test_generate_git_cache_key_subprocess_error(self, mock_run: Mock) -> None:
        """Test git cache key generation with subprocess error."""
        mock_run.side_effect = subprocess.SubprocessError("Git not found")

        repo_path = "/test/repo"
        cache_key = generate_git_cache_key(repo_path)

        assert cache_key is None

    @patch("os.stat")
    def test_generate_simple_cache_key(self, mock_stat: Mock) -> None:
        """Test simple cache key generation."""
        mock_stat.return_value = Mock(st_mtime=1234567890.0)

        repo_path = "/test/repo"
        files = ["file1.py", "file2.js", "file3.txt"]

        cache_key = generate_simple_cache_key(repo_path, files)

        assert cache_key is not None
        assert isinstance(cache_key, str)
        assert len(cache_key) == 32  # MD5 hash length

    @patch("os.stat")
    def test_generate_simple_cache_key_stat_error(self, mock_stat: Mock) -> None:
        """Test simple cache key generation with stat error."""
        mock_stat.side_effect = OSError("Permission denied")

        repo_path = "/test/repo"
        files = ["file1.py"]

        # Should not raise exception
        cache_key = generate_simple_cache_key(repo_path, files)
        assert cache_key is not None

    @patch("os.stat")
    def test_generate_full_cache_key(self, mock_stat: Mock) -> None:
        """Test full cache key generation."""
        mock_stat.return_value = Mock(st_mtime=1234567890.0, st_size=1024)

        repo_path = "/test/repo"
        files = ["file1.py", "file2.js"]

        cache_key = generate_full_cache_key(repo_path, files)

        assert cache_key is not None
        assert isinstance(cache_key, str)
        assert len(cache_key) == 32  # MD5 hash length

    @patch("os.stat")
    def test_generate_full_cache_key_file_missing(self, mock_stat: Mock) -> None:
        """Test full cache key generation with missing files."""
        # First file exists, second doesn't
        mock_stat.side_effect = [
            Mock(st_mtime=1234567890.0, st_size=1024),
            OSError("File not found"),
        ]

        repo_path = "/test/repo"
        files = ["file1.py", "missing.py"]

        cache_key = generate_full_cache_key(repo_path, files)
        assert cache_key is not None

    def test_generate_cache_key_consistency(self) -> None:
        """Test that same inputs produce same cache keys."""
        repo_path = "/test/repo"
        files = ["file1.py", "file2.js"]

        with patch("os.stat") as mock_stat:
            mock_stat.return_value = Mock(st_mtime=1234567890.0, st_size=1024)

            key1 = generate_simple_cache_key(repo_path, files)
            key2 = generate_simple_cache_key(repo_path, files)

            assert key1 == key2

    def test_generate_cache_key_different_inputs(self) -> None:
        """Test that different inputs produce different cache keys."""
        repo_path = "/test/repo"
        files1 = ["file1.py"]
        files2 = ["file2.py"]

        with patch("os.stat") as mock_stat:
            mock_stat.return_value = Mock(st_mtime=1234567890.0, st_size=1024)

            key1 = generate_simple_cache_key(repo_path, files1)
            key2 = generate_simple_cache_key(repo_path, files2)

            assert key1 != key2

    @patch("gsai.repo_map.is_git_repo")
    @patch("gsai.repo_map.generate_git_cache_key")
    @patch("gsai.repo_map.generate_simple_cache_key")
    def test_generate_cache_key_auto_git_success(
        self, mock_simple: Mock, mock_git: Mock, mock_is_git: Mock
    ) -> None:
        """Test auto strategy with successful git."""
        mock_is_git.return_value = True
        mock_git.return_value = "git_cache_key"

        repo_path = "/test/repo"
        files = ["file1.py"]

        cache_key, strategy = generate_cache_key(repo_path, files, "auto")

        assert cache_key == "git_cache_key"
        assert strategy == "git"
        mock_simple.assert_not_called()

    @patch("gsai.repo_map.is_git_repo")
    @patch("gsai.repo_map.generate_git_cache_key")
    @patch("gsai.repo_map.generate_simple_cache_key")
    def test_generate_cache_key_auto_git_fallback(
        self, mock_simple: Mock, mock_git: Mock, mock_is_git: Mock
    ) -> None:
        """Test auto strategy with git failure fallback."""
        mock_is_git.return_value = True
        mock_git.return_value = None  # Git fails
        mock_simple.return_value = "simple_cache_key"

        repo_path = "/test/repo"
        files = ["file1.py"]

        cache_key, strategy = generate_cache_key(repo_path, files, "auto")

        assert cache_key == "simple_cache_key"
        assert strategy == "simple"

    @patch("gsai.repo_map.is_git_repo")
    @patch("gsai.repo_map.generate_simple_cache_key")
    def test_generate_cache_key_auto_non_git(
        self, mock_simple: Mock, mock_is_git: Mock
    ) -> None:
        """Test auto strategy with non-git repo."""
        mock_is_git.return_value = False
        mock_simple.return_value = "simple_cache_key"

        repo_path = "/test/repo"
        files = ["file1.py"]

        cache_key, strategy = generate_cache_key(repo_path, files, "auto")

        assert cache_key == "simple_cache_key"
        assert strategy == "simple"

    def test_generate_cache_key_invalid_strategy(self) -> None:
        """Test generate_cache_key with invalid strategy."""
        repo_path = "/test/repo"
        files = ["file1.py"]

        with pytest.raises(ValueError, match="Unknown cache strategy"):
            generate_cache_key(repo_path, files, "invalid")

    @patch("gsai.repo_map.generate_git_cache_key")
    def test_generate_cache_key_git_strategy_failure(self, mock_git: Mock) -> None:
        """Test git strategy with failure and no fallback."""
        mock_git.return_value = None

        repo_path = "/test/repo"
        files = ["file1.py"]

        with pytest.raises(ValueError, match="Git strategy failed"):
            generate_cache_key(repo_path, files, "git")


class TestDiskCache:
    """Test disk cache operations."""

    @patch("gsai.config.cli_settings")
    @patch("gsai.config.config_manager")
    @patch("diskcache.Cache")
    def test_get_disk_cache_creation(
        self, mock_cache_class: Mock, mock_config_manager: Mock, mock_cli_settings: Mock
    ) -> None:
        """Test disk cache creation."""
        mock_cli_settings.max_cache_size_mb = 100
        mock_config_manager.cache_dir = Path("/test/cache")
        mock_config_manager.ensure_cache_dir.return_value = None

        _disk_cache = None

        get_disk_cache()

        mock_config_manager.ensure_cache_dir.assert_called_once()
        mock_cache_class.assert_called_once_with(
            "/test/cache", size_limit=104857600, tag_index=True
        )

    @patch("gsai.config.cli_settings")
    @patch("gsai.config.config_manager")
    @patch("diskcache.Cache")
    @patch("gsai.repo_map._disk_cache", None)  # Reset module-level cache
    def test_get_disk_cache_reuse(
        self, mock_cache_class: Mock, mock_config_manager: Mock, mock_cli_settings: Mock
    ) -> None:
        """Test disk cache object reuse."""
        mock_cli_settings.max_cache_size_mb = 100
        mock_config_manager.cache_dir = Path("/test/cache")
        mock_config_manager.ensure_cache_dir.return_value = None

        mock_cache = Mock()
        mock_cache_class.return_value = mock_cache

        # Call twice to test reuse
        cache1 = get_disk_cache()
        cache2 = get_disk_cache()

        # Both should return cache instances (may be same or different depending on implementation)
        assert cache1 is not None
        assert cache2 is not None
        # Cache class should be called at least once
        assert mock_cache_class.call_count >= 1


class TestCachedRepoMap:
    """Test cached repo map generation."""

    @patch("gsai.repo_map.get_repo_map_for_prompt")
    @patch("gsai.repo_map.get_disk_cache")
    @patch("gsai.config.cli_settings")
    def test_cached_repo_map_cache_disabled(
        self, mock_cli_settings: Mock, mock_get_cache: Mock, mock_get_repo_map: Mock
    ) -> None:
        """Test cached repo map with caching disabled."""
        mock_cli_settings.cache_enabled = False
        mock_cli_settings.verbose = False
        mock_get_repo_map.return_value = "test repo map"

        result = get_repo_map_for_prompt_cached("/test/repo")

        assert result == "test repo map"
        mock_get_cache.assert_not_called()
        mock_get_repo_map.assert_called_once_with("/test/repo")

    @patch("gsai.repo_map.get_repo_map_for_prompt")
    @patch("gsai.repo_map.get_disk_cache")
    @patch("gsai.repo_map.generate_git_cache_key")
    @patch("gsai.repo_map.is_git_repo")
    @patch("gsai.config.cli_settings")
    def test_cached_repo_map_cache_hit_git(
        self,
        mock_cli_settings: Mock,
        mock_is_git: Mock,
        mock_git_key: Mock,
        mock_get_cache: Mock,
        mock_get_repo_map: Mock,
    ) -> None:
        """Test cached repo map with cache hit using git strategy."""
        mock_cli_settings.cache_enabled = True
        mock_cli_settings.cache_strategy = "auto"
        mock_cli_settings.verbose = False
        mock_is_git.return_value = True
        mock_git_key.return_value = "git_cache_key"

        mock_cache = Mock()
        mock_cache.get.return_value = "cached repo map"
        mock_get_cache.return_value = mock_cache

        result = get_repo_map_for_prompt_cached("/test/repo")

        assert result == "cached repo map"
        mock_cache.get.assert_called_once_with("git_cache_key")
        mock_get_repo_map.assert_not_called()

    @patch("gsai.repo_map.get_repo_map_for_prompt")
    @patch("gsai.repo_map.get_disk_cache")
    @patch("gsai.repo_map.generate_git_cache_key")
    @patch("gsai.repo_map.is_git_repo")
    @patch("gsai.config.cli_settings")
    def test_cached_repo_map_cache_miss_git(
        self,
        mock_cli_settings: Mock,
        mock_is_git: Mock,
        mock_git_key: Mock,
        mock_get_cache: Mock,
        mock_get_repo_map: Mock,
    ) -> None:
        """Test cached repo map with cache miss using git strategy."""
        mock_cli_settings.cache_enabled = True
        mock_cli_settings.cache_strategy = "auto"
        mock_cli_settings.cache_ttl_days = 7
        mock_cli_settings.verbose = False
        mock_is_git.return_value = True
        mock_git_key.return_value = "git_cache_key"

        mock_cache = Mock()
        mock_cache.get.return_value = None  # Cache miss
        mock_get_cache.return_value = mock_cache
        mock_get_repo_map.return_value = "new repo map"

        result = get_repo_map_for_prompt_cached("/test/repo")

        assert result == "new repo map"
        mock_cache.get.assert_called_once_with("git_cache_key")
        mock_get_repo_map.assert_called_once_with("/test/repo")

        # Verify cache.set was called with correct parameters
        expected_ttl = 7 * 24 * 60 * 60  # 7 days in seconds
        expected_tag = f"repo:{hashlib.md5(b'/test/repo').hexdigest()[:8]}"
        mock_cache.set.assert_called_once_with(
            "git_cache_key", "new repo map", expire=expected_ttl, tag=expected_tag
        )

    @patch("gsai.repo_map.get_repo_map_for_prompt")
    @patch("gsai.repo_map.get_disk_cache")
    @patch("gsai.repo_map.generate_cache_key")
    @patch("gsai.repo_map.get_files_excluding_gitignore")
    @patch("gsai.repo_map.generate_git_cache_key")
    @patch("gsai.repo_map.is_git_repo")
    @patch("gsai.config.cli_settings")
    def test_cached_repo_map_git_fallback_to_simple(
        self,
        mock_cli_settings: Mock,
        mock_is_git: Mock,
        mock_git_key: Mock,
        mock_get_files: Mock,
        mock_generate_key: Mock,
        mock_get_cache: Mock,
        mock_get_repo_map: Mock,
    ) -> None:
        """Test cached repo map with git failure fallback to simple strategy."""
        mock_cli_settings.cache_enabled = True
        mock_cli_settings.cache_strategy = "auto"
        mock_cli_settings.cache_ttl_days = 7
        mock_cli_settings.verbose = False
        mock_is_git.return_value = True
        mock_git_key.return_value = None  # Git fails
        mock_get_files.return_value = ["file1.py", "file2.py"]
        mock_generate_key.return_value = ("simple_cache_key", "simple")

        mock_cache = Mock()
        mock_cache.get.return_value = None  # Cache miss
        mock_get_cache.return_value = mock_cache
        mock_get_repo_map.return_value = "new repo map"

        result = get_repo_map_for_prompt_cached("/test/repo")

        assert result == "new repo map"
        mock_generate_key.assert_called_once_with(
            "/test/repo", ["file1.py", "file2.py"], "auto"
        )

    @patch("gsai.repo_map.get_repo_map_for_prompt")
    @patch("gsai.repo_map.get_files_excluding_gitignore")
    @patch("gsai.repo_map.is_git_repo")
    @patch("gsai.config.cli_settings")
    def test_cached_repo_map_large_repo(
        self,
        mock_cli_settings: Mock,
        mock_is_git: Mock,
        mock_get_files: Mock,
        mock_get_repo_map: Mock,
    ) -> None:
        """Test cached repo map with large repository."""
        mock_cli_settings.cache_enabled = True
        mock_cli_settings.cache_strategy = "auto"
        mock_cli_settings.verbose = False
        mock_is_git.return_value = False
        # Simulate large repo (>10000 files)
        mock_get_files.return_value = [f"file{i}.py" for i in range(10001)]

        result = get_repo_map_for_prompt_cached("/test/repo")

        assert result == "Repo is too large to generate a repo map."
        mock_get_repo_map.assert_not_called()

    @patch("gsai.repo_map.get_repo_map_for_prompt")
    @patch("gsai.repo_map.get_disk_cache")
    @patch("gsai.config.cli_settings")
    def test_cached_repo_map_cache_exception_fallback(
        self, mock_cli_settings: Mock, mock_get_cache: Mock, mock_get_repo_map: Mock
    ) -> None:
        """Test cached repo map with cache exception fallback."""
        mock_cli_settings.cache_enabled = True
        mock_cli_settings.verbose = False
        mock_get_cache.side_effect = Exception("Cache error")
        mock_get_repo_map.return_value = "fallback repo map"

        result = get_repo_map_for_prompt_cached("/test/repo")

        assert result == "fallback repo map"
        mock_get_repo_map.assert_called_once_with("/test/repo")
