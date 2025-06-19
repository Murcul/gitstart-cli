from loguru import logger
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, Tool

from gsai.agents.models import (
    get_model_settings_by_model_name,
    get_pydantic_ai_model_by_model_name,
)
from gsai.agents.prompts.helpers import process_template
from gsai.agents.tools import ThinkingDeps, sequential_thinking
from gsai.agents.tools_agentic.extract_relevant_context_from_url import (
    extract_relevant_context_from_url,
)
from gsai.agents.tools_agentic.web_search import web_search
from gsai.config import cli_settings
from gsai.display_helpers import with_progress_display_async
from gsai.utils import safe_str_for_log


class WebNavigationDeps(ThinkingDeps):
    pass


class WebNavigationOutput(BaseModel):
    """respond with relevant context found from the web searches you have made"""

    relevant_context: str = Field(
        description="A good summary of the most relevant context found from your searches and internet travels. Ensure to include critical documentation when you find it."
    )
    links_visited: list[str] = Field(
        description="Every link visited during navigating the web"
    )
    search_queries_made: list[str] = Field(
        description="Every search query made during navigating the web"
    )


web_navigation_agent: Agent[WebNavigationDeps, WebNavigationOutput] = Agent(
    model=get_pydantic_ai_model_by_model_name(cli_settings.WEB_SEARCH_AGENT_MODEL_NAME),
    deps_type=WebNavigationDeps,
    tools=[
        sequential_thinking,
        Tool(extract_relevant_context_from_url, takes_ctx=True),
        Tool(web_search, takes_ctx=True),
    ],
    output_type=WebNavigationOutput,
    retries=5,
    output_retries=5,
)


@web_navigation_agent.system_prompt
def system_prompt(ctx: RunContext[WebNavigationDeps]) -> str:
    return process_template("web_navigation_system.jinja", {})


@with_progress_display_async("web_navigation", "Navigating the web")
async def web_navigation(
    ctx: RunContext[WebNavigationDeps], prompt: str
) -> WebNavigationOutput:
    """
    Navigate the web through urls or searches

    IMPORTANT: useful for getting documentation through links or searching through the web for documentation, api definitions, etc.

    <Example Prompt>
      Here is an intent description that may contain urls:
          <INTENT></INTENT>
        I need to know about the ast-grep documentation so that I can understand how to use it lint a repo.
    </Example Prompt>

    <Example Prompt>
      Here is an intent description that may contain urls:
          <INTENT></INTENT>
        Can you let me know what key documentation is contained at https://docs.temporal.io?
    </Example Prompt>

    <Example Prompt>
        Here is an intent description that may contain urls:
        <INTENT></INTENT>
        I need to understand how to use uv correctly, here's the readme: https://github.com/astral-sh/uv-docker-example/blob/main/README.md but also maybe make some searches.
    </Example Prompt>

    Args:
        ctx: The run context containing dependencies.
        prompt: The prompt to send to the web navigation agent.

    Returns:
        The relevant context retrieved from the web navigation agent.
    """
    logger.info(safe_str_for_log(f"Web Navigation Prompt: {prompt}"))
    result = await web_navigation_agent.run(
        process_template(
            "web_navigation.jinja",
            {
                "prompt": prompt,
            },
        ),
        deps=ctx.deps,
        model_settings=get_model_settings_by_model_name(
            cli_settings.WEB_NAVIGATION_AGENT_MODEL_NAME
        ),
    )
    output = result.output
    usage = result.usage()

    logger.info(safe_str_for_log(f"Web Navigation usage: {usage}"))
    return output
