from typing import Annotated

from annotated_types import MinLen
from loguru import logger
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, Tool

from gsai.agents.models import (
    get_model_settings_by_model_name,
    get_pydantic_ai_model_by_model_name,
)
from gsai.agents.prompts.helpers import process_template
from gsai.agents.tools import (
    ThinkingDeps,
    list_files,
    quick_view_file,
    search_for_code,
    search_for_files,
    sequential_thinking,
    view_file,
)
from gsai.config import cli_settings
from gsai.display_helpers import with_progress_display_async
from gsai.utils import safe_str_for_log


class ExpertDeps(ThinkingDeps):
    pass


class ExpertOutput(BaseModel):
    """respond with advice about the problem you have been asked"""

    advice: Annotated[str, MinLen(1)] = Field(
        description="This is the advice/answer the expert gives based on what you asked them."
    )


expert_agent: Agent[ExpertDeps, ExpertOutput] = Agent(
    model=get_pydantic_ai_model_by_model_name(cli_settings.EXPERT_AGENT_MODEL_NAME),
    deps_type=ExpertDeps,
    tools=[
        search_for_code,
        view_file,
        list_files,
        search_for_files,
        sequential_thinking,
        Tool(quick_view_file, name="quick_view_file"),
    ],
    output_type=ExpertOutput,
    retries=5,
    output_retries=5,
)


@expert_agent.system_prompt
def system_prompt(ctx: RunContext[ExpertDeps]) -> str:
    return process_template("expert_system.jinja", {})


@with_progress_display_async("expert", "Consulting expert AI")
async def expert(ctx: RunContext[ExpertDeps], prompt: str) -> ExpertOutput:
    """
    Ask a question to an expert AI model.

    Keep your questions specific, but long and detailed.

    You only query the expert when you have a specific question in mind.

    The expert can be extremely useful at logic questions, debugging, and reviewing complex source code, but you must provide all context including source manually.

    Try to phrase your question in a way that it does not expand the scope of our top-level task.

    The expert can be prone to overthinking depending on what and how you ask it.

    <Example Prompt>
      I just got a linting error, here it is:
          <ERROR></ERROR>
          <FILE CONTENTS><FILE CONTENTS>
        Any idea as to what this issue is?
    </Example Prompt>

    <Example Prompt>
      Struggling to understand how best to structure this API Schema, any ideas?
          <INTENT></INTENT>
          <SPEC><SPEC>
    </Example Prompt>

    Args:
        ctx: The run context containing dependencies.
        prompt: The prompt to send to the expert agent.

    Returns:
        The advice given by the expert agent.
    """
    logger.info("Asking Expert for advice")
    result = await expert_agent.run(
        process_template(
            "expert.jinja",
            {
                "prompt": prompt,
            },
        ),
        deps=ctx.deps,
        model_settings=get_model_settings_by_model_name(
            cli_settings.EXPERT_AGENT_MODEL_NAME
        ),
    )
    output = result.output
    usage = result.usage()
    logger.info(
        safe_str_for_log(f"Expert usage: {usage}"),
    )

    return output
