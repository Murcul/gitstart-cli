"""CLI-specific code writing agent with security validation."""

from typing import Annotated

from annotated_types import MinLen
from loguru import logger
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, Tool

from gsai.agents.models import get_pydantic_ai_model_by_model_name
from gsai.agents.prompts.helpers import process_template
from gsai.agents.tools import (  # search_codebase_natural_language,
    list_files,
    move_file,
    overwrite_file,
    quick_view_file,
    run_command,
    save_to_memory,
    search_for_code,
    search_for_files,
    sequential_thinking,
    str_replace,
    view_file,
)
from gsai.agents.tools.deps import FileToolDeps
from gsai.agents.tools_agentic.expert import expert
from gsai.config import cli_settings


class CodeWritingAgentOutput(BaseModel):
    """Ensure to respond with a summary of all changes made, a best-practices commit,
    a PR description in prosemirror doc json format, a pr description in markdown format, all files modified, and all files created"""

    summary: Annotated[str, MinLen(1)] = Field(
        description="A summary of all changes made to the codebase"
    )
    commit_message: Annotated[str, MinLen(1)] = Field(
        description="A commit message that will be used when committing the code through git"
    )
    pull_request_description_markdown: str = Field(
        description="A description that will be used for the pull request in GitHub Flavored Markdown"
    )
    files_modified: list[str] = Field(description="A list of files that were modified")
    files_created: list[str] = Field(description="A list of files that were created")


class CodeWritingAgentDeps(FileToolDeps):
    """Dependencies for the CLI code writing agent."""

    pass


logger.info(get_pydantic_ai_model_by_model_name(cli_settings.CODING_AGENT_MODEL_NAME))
code_writing_agent: Agent[CodeWritingAgentDeps, CodeWritingAgentOutput] = Agent(
    model=get_pydantic_ai_model_by_model_name(cli_settings.CODING_AGENT_MODEL_NAME),
    deps_type=CodeWritingAgentDeps,
    tools=[
        # search_codebase_natural_language,
        search_for_code,
        view_file,
        quick_view_file,
        list_files,
        search_for_files,
        Tool(str_replace, max_retries=5, takes_ctx=True),
        sequential_thinking,
        Tool(move_file, max_retries=5, takes_ctx=True),
        Tool(overwrite_file, max_retries=5, takes_ctx=True),
        Tool(run_command, max_retries=3, takes_ctx=True),
        Tool(expert, takes_ctx=True),
        Tool(save_to_memory, takes_ctx=True),
    ],
    output_type=CodeWritingAgentOutput,
    retries=5,
    output_retries=5,
)


@code_writing_agent.instructions
def code_writing_instructions(ctx: RunContext[CodeWritingAgentDeps]) -> str:
    return process_template(
        "coding_instructions.jinja",
        {
            "ctx": ctx,
        },
    )
