"""CLI-specific implementation planning agent with security validation."""

from typing import Annotated

from annotated_types import MinLen
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, Tool

from gsai.agents.models import get_pydantic_ai_model_by_model_name
from gsai.agents.prompts.helpers import process_template
from gsai.agents.tools import (  # search_codebase_natural_language,
    list_files,
    quick_view_file,
    save_to_memory,
    search_for_code,
    search_for_files,
    view_file,
)
from gsai.agents.tools.deps import CodebaseDeps

# from ai_cli.agents.tools import sequential_thinking
from gsai.agents.tools_agentic.expert import expert
from gsai.config import cli_settings


class ImplementationPlanningAgentOutput(BaseModel):
    """respond with an implementation plan"""

    implementation_plan: Annotated[str, MinLen(1)] = Field(
        description="A detailed implementation plan in Markdown format with steps, considerations, and acceptance criteria"
    )
    estimated_complexity: str = Field(
        description="Estimated complexity level (Low, Medium, High) with brief justification"
    )
    key_files_to_modify: list[str] = Field(
        description="List of key files that will likely need modification"
    )
    dependencies_needed: list[str] = Field(
        description="List of new dependencies or tools that might be needed"
    )


class ImplementationPlanningAgentDeps(CodebaseDeps):
    """Dependencies for the CLI implementation planning agent."""

    pass


implementation_planning_agent: Agent[
    ImplementationPlanningAgentDeps, ImplementationPlanningAgentOutput
] = Agent(
    model=get_pydantic_ai_model_by_model_name(
        cli_settings.IMPLEMENTATION_PLAN_AGENT_MODEL_NAME
    ),
    deps_type=ImplementationPlanningAgentDeps,
    tools=[
        # search_codebase_natural_language,
        search_for_code,
        view_file,
        quick_view_file,
        list_files,
        search_for_files,
        # sequential_thinking,
        Tool(expert, takes_ctx=True),
        Tool(save_to_memory, takes_ctx=True),
    ],
    output_type=ImplementationPlanningAgentOutput,
    retries=5,
    output_retries=5,
)


@implementation_planning_agent.instructions
def implementation_planning_instructions(
    ctx: RunContext[ImplementationPlanningAgentDeps],
) -> str:
    return process_template("implementation_plan_system.jinja", {"ctx": ctx})
