try:
    from gsai.build_config import EMBEDDED_OPENAI_API_KEY, EMBEDDED_ANTHROPIC_API_KEY
except ImportError:
    EMBEDDED_OPENAI_API_KEY = ''
    EMBEDDED_ANTHROPIC_API_KEY = ''

"""CLI-specific configuration extending base settings."""

import logging
import os
import pathlib
import shutil
import stat
import sys
from enum import StrEnum, auto
from typing import TYPE_CHECKING, Literal, TypedDict

import httpx
from loguru import logger
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    from loguru import Record
ROOT = pathlib.Path(__file__).resolve().parent.parent
DOTENV = pathlib.Path(ROOT, ".env")

# Global configuration paths
GLOBAL_CONFIG_DIR = pathlib.Path.home() / ".ai" / "gsai"
GLOBAL_DOTENV = GLOBAL_CONFIG_DIR / ".env"


class GSEnvs(StrEnum):
    DEVELOPMENT = auto()
    STAGING = auto()
    PRODUCTION = auto()


class PublicKey(TypedDict):
    crv: str
    x: str
    kty: str


class PrivateKey(TypedDict):
    crv: str
    d: str
    x: str
    kty: str


class ConfigManager:
    """Manages global configuration for the CLI."""

    def __init__(self) -> None:
        self.global_config_dir = GLOBAL_CONFIG_DIR
        self.global_config_file = GLOBAL_DOTENV
        self.cache_dir = self.global_config_dir / "cache"

    def ensure_global_config_dir(self) -> None:
        """Create global config directory with secure permissions."""
        try:
            self.global_config_dir.mkdir(parents=True, exist_ok=True)
            # Set secure permissions (700 - owner read/write/execute only)
            os.chmod(self.global_config_dir, stat.S_IRWXU)
        except Exception as e:
            logger.warning(f"Failed to create global config directory: {e}")

    def ensure_cache_dir(self) -> None:
        """Create cache directory with secure permissions."""
        try:
            self.ensure_global_config_dir()
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            # Set secure permissions (700 - owner read/write/execute only)
            os.chmod(self.cache_dir, stat.S_IRWXU)
        except Exception as e:
            logger.warning(f"Failed to create cache directory: {e}")

    def clear_cache(self) -> bool:
        """Clear all cached data."""
        try:
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.ensure_cache_dir()
                return True
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

    def get_cache_info(self) -> dict[str, str]:
        """Get cache directory information."""
        cache_info = {
            "cache_dir": str(self.cache_dir),
            "cache_exists": str(self.cache_dir.exists()),
            "cache_size": "0 MB",
            "cache_entries": "0",
        }

        if self.cache_dir.exists():
            try:
                total_size = 0
                entry_count = 0
                for dirpath, dirnames, filenames in os.walk(self.cache_dir):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        try:
                            total_size += os.path.getsize(filepath)
                            entry_count += 1
                        except OSError:
                            continue

                cache_info["cache_size"] = f"{total_size / (1024 * 1024):.1f} MB"
                cache_info["cache_entries"] = str(entry_count)
            except Exception:
                pass

        return cache_info

    def save_api_key(self, key_name: str, key_value: str) -> bool:
        """Save an API key to global configuration."""
        try:
            self.ensure_global_config_dir()

            # Read existing config
            config_data = {}
            if self.global_config_file.exists():
                with open(self.global_config_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and "=" in line and not line.startswith("#"):
                            key, value = line.split("=", 1)
                            config_data[key] = value

            # Update with new key
            config_data[key_name] = key_value

            # Write back to file atomically
            temp_file = self.global_config_file.with_suffix(".tmp")
            with open(temp_file, "w") as f:
                for key, value in config_data.items():
                    f.write(f"{key}={value}\n")

            # Set secure permissions (600 - owner read/write only)
            os.chmod(temp_file, stat.S_IRUSR | stat.S_IWUSR)

            # Atomic move
            temp_file.replace(self.global_config_file)
            return True

        except Exception as e:
            logger.error(f"Failed to save API key {key_name}: {e}")
            return False

    def get_config_status(self) -> dict[str, str]:
        """Get status of global configuration."""
        status = {
            "global_config_dir": str(self.global_config_dir),
            "global_config_exists": str(self.global_config_file.exists()),
            "global_config_readable": "False",
            "openai_key_configured": "False",
            "anthropic_key_configured": "False",
        }

        if self.global_config_file.exists():
            try:
                with open(self.global_config_file) as f:
                    content = f.read()
                    status["global_config_readable"] = "True"
                    status["openai_key_configured"] = str("OPENAI_API_KEY=" in content)
                    status["anthropic_key_configured"] = str(
                        "ANTHROPIC_API_KEY=" in content
                    )
            except Exception:
                pass

        # Add cache information
        cache_info = self.get_cache_info()
        status.update(cache_info)

        # Add agent model configurations
        agent_models = self._get_agent_models()
        status["agent_models"] = str(len(agent_models)) + " categories configured"

        return status

    def _get_agent_models(self) -> dict[str, dict[str, dict[str, str]]]:
        """Get categorized agent model configurations."""
        from gsai.config import cli_settings

        def parse_model_name(model_name: str) -> tuple[str, str]:
            """Parse provider:model format, return (provider, model)."""
            if ":" in model_name:
                provider, model = model_name.split(":", 1)
                return provider.title(), model
            return "Unknown", model_name

        # Categorize agent models
        core_agents = {
            "Coding Agent": cli_settings.CODING_AGENT_MODEL_NAME,
            "Implementation Plan Agent": cli_settings.IMPLEMENTATION_PLAN_AGENT_MODEL_NAME,
            "Spec Agent": cli_settings.SPEC_AGENT_MODEL_NAME,
            "HLD Agent": cli_settings.HLD_AGENT_MODEL_NAME,
        }

        web_search_agents = {
            "Web Navigation Agent": cli_settings.WEB_NAVIGATION_AGENT_MODEL_NAME,
            "Web Search Agent": cli_settings.WEB_SEARCH_AGENT_MODEL_NAME,
            "Extract Context Agent": cli_settings.EXTRACT_CONTEXT_FROM_URL_AGENT_MODEL_NAME,
            "Research Agent": cli_settings.RESEARCH_AGENT_MODEL_NAME,
        }

        specialized_agents = {
            "Expert Agent": cli_settings.EXPERT_AGENT_MODEL_NAME,
            "Ticket Writing Agent": cli_settings.TICKET_WRITING_AGENT_MODEL_NAME,
        }

        cli_agents = {
            "CLI Master Agent": cli_settings.CLI_MASTER_AGENT_MODEL_NAME,
            "Question Answering Agent": cli_settings.QUESTION_ANSWERING_AGENT_MODEL_NAME,
            "Git Operations Agent": cli_settings.GIT_OPERATIONS_AGENT_MODEL_NAME,
        }

        # Convert to categorized format with parsed provider/model
        categorized_models: dict[str, dict[str, dict[str, str]]] = {}
        for category, agents in [
            ("Core Agents", core_agents),
            ("Web & Search Agents", web_search_agents),
            ("Specialized Agents", specialized_agents),
            ("CLI Agents", cli_agents),
        ]:
            categorized_models[category] = {}
            for agent_name, model_name in agents.items():
                provider, model = parse_model_name(model_name)
                categorized_models[category][agent_name] = {
                    "provider": provider,
                    "model": model,
                    "full_name": model_name,
                }

        return categorized_models

    def migrate_local_to_global(self, local_env_path: pathlib.Path) -> bool:
        """Migrate configuration from local .env to global config."""
        try:
            if not local_env_path.exists():
                return False

            self.ensure_global_config_dir()

            # Read local config
            with open(local_env_path) as f:
                local_content = f.read()

            # Extract API keys
            api_keys = {}
            for line in local_content.split("\n"):
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    if key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]:
                        api_keys[key] = value

            # Save to global config
            for key, value in api_keys.items():
                self.save_api_key(key, value)

            return len(api_keys) > 0

        except Exception as e:
            logger.error(f"Failed to migrate config: {e}")
            return False

    async def validate_api_key(self, key_type: str, api_key: str) -> bool:
        """Validate an API key by making a test request."""
        try:
            if key_type == "openai":
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "https://api.openai.com/v1/models",
                        headers={"Authorization": f"Bearer {api_key}"},
                        timeout=10.0,
                    )
                    return response.status_code == 200
            elif key_type == "anthropic":
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "x-api-key": api_key,
                            "anthropic-version": "2023-06-01",
                            "content-type": "application/json",
                        },
                        json={
                            "model": "claude-3-haiku-20240307",
                            "max_tokens": 1,
                            "messages": [{"role": "user", "content": "test"}],
                        },
                        timeout=10.0,
                    )
                    return response.status_code in [
                        200,
                        400,
                    ]  # 400 is ok for validation
            return False
        except Exception:
            return False


class Settings(BaseSettings):
    ENV: str = Field(
        default=GSEnvs.DEVELOPMENT, description="Environment application is running in."
    )
    LOG_LEVEL: str = Field(default="DEBUG", description="Logging level")

    # Gateway/Service Type Beats
    PUBLIC_KEY: PublicKey = Field(
        default=PublicKey(crv="", x="", kty=""), description="Public Key"
    )
    PRIVATE_KEY: PrivateKey = Field(
        default=PrivateKey(crv="", d="", x="", kty=""), description="Private Key"
    )
    GATEWAY_API_URL: str = Field(
        default="http://0.0.0.0:4500", description="URL for the GS Gateway"
    )
    SERVICE_NAME: str = Field(
        default="orchestrator", description="Service identifier for gateway registrtion"
    )

    # DB
    DATABASE_URL: str = Field(
        default="", description="Database fully qualified connection string"
    )

    # SENTRY
    SENTRY_DSN: str = Field(default="", description="Sentry DSN")
    SENTRY_WORKER_DSN: str = Field(default="", description="Sentry Worker DSN")

    # Temporal connection settings
    TEMPORAL_ADDRESS: str = Field(
        default="localhost:7233", description="Temporal Server URL"
    )
    TEMPORAL_NAMESPACE: str = Field(default="default", description="Temporal Namespace")
    TEMPORAL_TASK_QUEUE: str = Field(
        default="agent-task-queue", description="Temporal Task Queue Name"
    )

    # Temporal Authentication settings
    TEMPORAL_API_KEY: str = Field(default="", description="Temporal API Key")

    AI_INTENT_THREAD_ENABLED_LIST: list[str] = Field(
        default=[],
        description="A list of instance ids that indicate instances that allow AI INTENT THREADS",
    )

    # MODELS TO USE
    CODING_AGENT_MODEL_NAME: str = Field(
        default="anthropic:claude-3-7-sonnet-latest",
        description="Model to use for Coding Agent, prefix with lowercase company name",
    )
    SPEC_AGENT_MODEL_NAME: str = Field(
        default="anthropic:claude-3-7-sonnet-latest",
        description="Model to use for Intent to Spec Agent, prefix with lowercase company name",
    )
    RESEARCH_AGENT_MODEL_NAME: str = Field(
        default="anthropic:claude-3-7-sonnet-latest",
        description="Model to use for Research Agent, prefix with lowercase company name",
    )
    HLD_AGENT_MODEL_NAME: str = Field(
        default="anthropic:claude-3-7-sonnet-latest",
        description="Model to use for High Level Design Agent, prefix with lowercase company name",
    )
    IMPLEMENTATION_PLAN_AGENT_MODEL_NAME: str = Field(
        default="anthropic:claude-3-7-sonnet-latest",
        description="Model to use for Implementation Plan Agent, prefix with lowercase company name",
    )
    WEB_NAVIGATION_AGENT_MODEL_NAME: str = Field(
        default="anthropic:claude-3-7-sonnet-latest",
        description="Model to use for Web Navigation Agent, prefix with lowercase company name",
    )
    WEB_SEARCH_AGENT_MODEL_NAME: str = Field(
        default="anthropic:claude-3-7-sonnet-latest",
        description="Model to use for Search Agent, prefix with lowercase company name",
    )
    EXTRACT_CONTEXT_FROM_URL_AGENT_MODEL_NAME: str = Field(
        default="anthropic:claude-3-7-sonnet-latest",
        description="Model to use for ExtractContextFromURLs, prefix with lowercase company name",
    )
    EXPERT_AGENT_MODEL_NAME: str = Field(
        default="openai:o3-mini",
        description="Model to use for Expert Agent, prefix with lowercase company name",
    )
    TICKET_WRITING_AGENT_MODEL_NAME: str = Field(
        default="anthropic:claude-3-7-sonnet-latest",
        description="Model to use for Ticket Writing Agent, prefix with lowercase company name",
    )
    CLI_MASTER_AGENT_MODEL_NAME: str = Field(
        default="anthropic:claude-3-7-sonnet-latest",
        description="Model to use for CLI Master Agent, prefix with lowercase company name",
    )
    QUESTION_ANSWERING_AGENT_MODEL_NAME: str = Field(
        default="anthropic:claude-3-7-sonnet-latest",
        description="Model to use for CLI QUESTION ANSWER Agent, prefix with lowercase company name",
    )
    GIT_OPERATIONS_AGENT_MODEL_NAME: str = Field(
        default="anthropic:claude-3-7-sonnet-latest",
        description="Model to use for CLI GIT OPERATIONS Agent, prefix with lowercase company name",
    )

    # Model Keys
    OPENAI_API_KEY: str = Field(default=EMBEDDED_OPENAI_API_KEY or "", description="OpenAI API Key")
    ANTHROPIC_API_KEY: str = Field(default=EMBEDDED_ANTHROPIC_API_KEY or "", description="Anthropic API Key")

    # Where all repos should be stored
    REPOS_PATH: str = Field(
        default="/data/repos", description="Where all repos should be stored"
    )

    SLACK_BOT_TOKEN: str = Field(default="", description="For Slack Bolt App")
    SLACK_SIGNING_SECRET: str = Field(default="", description="For Slack Bolt App")
    SLACK_BOT_ID: str = Field(default="", description="For Slack Bolt App")

    model_config = SettingsConfigDict(env_file=[GLOBAL_DOTENV, DOTENV], extra="allow")


class CLISettings(Settings):
    """CLI-specific settings extending base Settings class."""

    approval_mode: Literal["suggest", "auto-edit", "full-auto"] = Field(
        default="suggest",
        description="Approval mode for CLI operations: suggest (read-only), auto-edit (can edit files), full-auto (can edit and run commands)",
    )
    working_directory: str = Field(
        default_factory=os.getcwd,
        description="Working directory for CLI operations - all operations are restricted to this directory",
    )
    web_search_enabled: bool = Field(
        default=False, description="Whether web search is enabled for the CLI agents"
    )
    verbose: bool = Field(
        default=False, description="Whether to show detailed logs and verbose output"
    )
    usage_limits: dict[str, int] = Field(
        default_factory=dict,
        description="Usage limits for CLI operations (tokens, requests, etc.)",
    )

    # Cache settings
    cache_enabled: bool = Field(
        default=True, description="Whether repo map caching is enabled"
    )
    cache_strategy: str = Field(
        default="auto",
        description="Cache strategy: 'auto' (git-based for git repos, simple for others), 'git', 'simple', 'full'",
    )
    cache_ttl_days: int = Field(default=30, description="Cache time-to-live in days")
    max_cache_size_mb: int = Field(
        default=1024, description="Maximum cache size in megabytes"
    )


class SecurityContext(BaseModel):
    """Security context for CLI operations."""

    working_directory: str
    approval_mode: Literal["suggest", "auto-edit", "full-auto"]
    web_search_enabled: bool
    verbose: bool = False

    def can_edit_files(self) -> bool:
        """Check if current approval mode allows file editing."""
        return self.approval_mode in ["auto-edit", "full-auto"]

    def can_run_commands(self) -> bool:
        """Check if current approval mode allows command execution."""
        return self.approval_mode == "full-auto"

    def requires_approval_for_files(self) -> bool:
        """Check if file operations require user approval."""
        return self.approval_mode == "suggest"

    def requires_approval_for_commands(self) -> bool:
        """Check if command execution requires user approval."""
        return self.approval_mode in ["suggest", "auto-edit"]


def formatter(record: "Record") -> str:
    internal_resource_id = record["extra"].get("internal_resource_id", None)
    if internal_resource_id is None:
        return (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>\n"
        )
    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level}</level> | "
        f"<yellow>{internal_resource_id}</yellow> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>\n"
    )


def configure_logging(verbose: bool = False) -> None:
    """Configure logging based on verbose mode setting."""
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    log_level = "ERROR"
    if verbose:
        log_level = "DEBUG"
    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "level": log_level,
                "format": formatter,
            }
        ]
    )


cli_settings = CLISettings()
config_manager = ConfigManager()

# Configure logging initially with the default verbose setting
configure_logging(cli_settings.verbose)
