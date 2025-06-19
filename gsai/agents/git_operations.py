"""CLI-specific git operations agent with security validation."""

from typing import Annotated

from annotated_types import MinLen
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, Tool

from gsai.agents.models import get_pydantic_ai_model_by_model_name
from gsai.agents.tools import cli_git_commit, cli_git_status
from gsai.agents.tools.deps import WriteToolDeps
from gsai.agents.tools_agentic.expert import expert
from gsai.config import cli_settings


class GitOperationsAgentOutput(BaseModel):
    """respond with a response for the user operations permformed and status info"""

    response: Annotated[str, MinLen(1)] = Field(
        description="A detailed response about the git operations performed"
    )
    operations_performed: list[str] = Field(
        description="List of git operations that were performed"
    )
    status_info: str = Field(default="", description="Current git status information")


class GitOperationsAgentDeps(WriteToolDeps):
    """Dependencies for the CLI git operations agent."""

    pass


git_operations_agent: Agent[GitOperationsAgentDeps, GitOperationsAgentOutput] = Agent(
    model=get_pydantic_ai_model_by_model_name(cli_settings.CODING_AGENT_MODEL_NAME),
    deps_type=GitOperationsAgentDeps,
    tools=[
        cli_git_status,
        cli_git_commit,
        # sequential_thinking,
        Tool(expert, takes_ctx=True),
    ],
    output_type=GitOperationsAgentOutput,
    retries=5,
    output_retries=5,
)


@git_operations_agent.instructions
def git_operations_system_prompt(ctx: RunContext[GitOperationsAgentDeps]) -> str:
    return f"""You are a git operations specialist working in a secure CLI environment. Your role is to perform git operations safely and efficiently.

## Environment Information:
- Working Directory: {ctx.deps.security_context.working_directory}
- Repository Path: {ctx.deps.repo_path}
- Approval Mode: {ctx.deps.security_context.approval_mode}

## Security Constraints:
- All git operations are restricted to the working directory
- Command execution requires approval based on the current approval mode
- You cannot access repositories outside the working directory

## Your Capabilities:
1. **Status Checking**: Check git status and repository state
2. **Committing**: Create commits with appropriate messages
3. **Repository Analysis**: Understand the current state of the repository

## Git Operations You Handle:
- **Status Checks**: "git status", "show current changes"
- **Committing**: "commit changes", "create commit with message"
- **Repository Info**: "show git log", "check branch status"

## Guidelines:
1. **Safety First**: Always check status before performing operations
2. **Clear Messages**: Use descriptive commit messages
3. **Approval Aware**: Respect the approval mode for command execution
4. **Informative**: Provide clear feedback about operations performed
5. **Error Handling**: Handle git errors gracefully and provide helpful messages

## Approval Mode Behavior:
- **suggest**: All git commands require user approval
- **auto-edit**: Git commands require user approval
- **full-auto**: Git commands can be executed without approval

## Best Practices:
- Always check git status before committing
- Use meaningful commit messages
- Provide clear feedback about what was done
- Handle edge cases (no changes, conflicts, etc.)

Remember: You are operating in a secure environment with approval workflows. Always respect the security context and provide clear explanations of git operations."""
