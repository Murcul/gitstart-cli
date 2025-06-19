"""Dependency types for AI Coding CLI tools."""

from typing import TYPE_CHECKING, Any

from git import Repo
from pydantic import BaseModel, ConfigDict, Field

from gsai.config import SecurityContext
from gsai.security import ApprovalManager

if TYPE_CHECKING:
    pass


class BaseDeps(BaseModel):
    """Base dependencies for all tools."""

    pass


class ThoughtData(BaseModel):
    """Data structure for sequential thinking."""

    thought: str
    thought_number: int
    total_thoughts: int
    next_thought_needed: bool
    is_revision: bool | None
    revises_thought: int | None
    branch_from_thought: int | None
    branch_id: str | None
    needs_more_thoughts: bool | None


class ThinkingDeps(BaseDeps):
    """Dependencies for tools that support sequential thinking."""

    thought_history: list[ThoughtData] = Field(default_factory=list)
    branches: dict[str, list[ThoughtData]] = Field(default_factory=dict)


class CodebaseDeps(ThinkingDeps):
    """Dependencies for tools that operate on codebases."""

    cache: dict[str, Any] = Field(default_factory=dict)
    security_context: SecurityContext
    approval_manager: ApprovalManager
    repo_path: str
    session_state: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class FileToolDeps(CodebaseDeps):
    """Dependencies for tools that can write/modify files without git integration."""

    model_config = ConfigDict(arbitrary_types_allowed=True)


class WriteToolDeps(CodebaseDeps):
    """Dependencies for tools that can write/modify files."""

    git_repo: Repo
    model_config = ConfigDict(arbitrary_types_allowed=True)
