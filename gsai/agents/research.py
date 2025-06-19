from typing import Annotated

from annotated_types import MinLen
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, Tool

from gsai.agents.models import get_pydantic_ai_model_by_model_name
from gsai.agents.prompts.helpers import process_template
from gsai.agents.tools import (
    list_files,
    quick_view_file,
    search_for_code,
    search_for_files,
    sequential_thinking,
    view_file,
)
from gsai.agents.tools.deps import CodebaseDeps
from gsai.agents.tools_agentic.expert import expert
from gsai.agents.tools_agentic.web_navigation import web_navigation
from gsai.config import cli_settings


class ResearchAgentOutput(BaseModel):
    """respond with a research_document, repo_information, important_paths, important_urls, and open_questions (if there are)"""

    research_document: Annotated[str, MinLen(1)] = Field(
        description="A research document that carefully puts together all the information required to move forward with a solution but does not include general information about the repository and codebase"
    )
    repo_information: Annotated[str, MinLen(1)] = Field(
        description="A subsection of the research document that carefully puts together all the information about the repository and codebase"
    )
    open_questions: list[str] = Field(
        [],
        description="Questions that need to be answered by the product manager/engineering lead in order to have the right context to move forward with a solution",
    )
    important_paths: dict[str, str] = Field(
        description="Important paths in the codebase (absolute or globs) mapped to a short summary as to why they are important context for the task at hand"
    )
    important_urls: dict[str, str] = Field(
        description="URLs that were important to the research mapped to a short summary as to why they are important context for the task at hand"
    )


class ResearchAgentDeps(CodebaseDeps):
    pass


research_agent: Agent[ResearchAgentDeps, ResearchAgentOutput] = Agent(
    model=get_pydantic_ai_model_by_model_name(cli_settings.RESEARCH_AGENT_MODEL_NAME),
    deps_type=ResearchAgentDeps,
    tools=[
        search_for_code,
        view_file,
        list_files,
        search_for_files,
        sequential_thinking,
        Tool(quick_view_file, name="quick_view_file"),
        Tool(web_navigation, takes_ctx=True),
        Tool(expert, takes_ctx=True),
    ],
    output_type=ResearchAgentOutput,
    retries=5,
    output_retries=5,
)


@research_agent.instructions
def instructions(ctx: RunContext[ResearchAgentDeps]) -> str:
    return process_template(
        "research_system.jinja",
        {},
    )
