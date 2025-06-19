import functools
from dataclasses import dataclass

import anyio
import anyio.to_thread
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import DuckDuckGoSearchException
from loguru import logger
from pydantic import BaseModel, Field, TypeAdapter
from pydantic_ai import Agent, RunContext, Tool
from typing_extensions import TypedDict

from gsai.agents.models import (
    get_model_settings_by_model_name,
    get_pydantic_ai_model_by_model_name,
)
from gsai.agents.prompts.helpers import process_template
from gsai.agents.tools import ThinkingDeps, sequential_thinking
from gsai.config import cli_settings
from gsai.display_helpers import with_progress_display_async
from gsai.utils import safe_str_for_log


class DuckDuckGoResult(TypedDict):
    """A DuckDuckGo search result."""

    title: str
    """The title of the search result."""
    href: str
    """The URL of the search result."""
    body: str
    """The body of the search result."""


duckduckgo_ta = TypeAdapter(list[DuckDuckGoResult])


class SearchAgentDeps(ThinkingDeps):
    pass


@dataclass
class DuckDuckGoSearchTool:
    """The DuckDuckGo search tool."""

    client: DDGS
    """The DuckDuckGo search client."""

    max_results: int | None = None
    """The maximum number of results. If None, returns results only from the first response."""

    async def __call__(
        self, ctx: RunContext[SearchAgentDeps], query: str
    ) -> list[DuckDuckGoResult]:
        """Searches DuckDuckGo for the given query and returns the results.

        Args:
            query: The query to search for.

        Returns:
            The search results.
        """
        logger.info(safe_str_for_log(f"Searching for {query}"))
        search = functools.partial(self.client.text, max_results=self.max_results)
        try:
            results = await anyio.to_thread.run_sync(search, query)
        except DuckDuckGoSearchException:
            return [
                DuckDuckGoResult(
                    title="ERROR: Rate Limited by DuckDuckGo Search, Please wait to search again",
                    href="ERROR: Rate Limited by DuckDuckGo Search, Please wait to search again",
                    body="ERROR: Rate Limited by DuckDuckGo Search, Please wait to search again",
                )
            ]
        return duckduckgo_ta.validate_python(results)


def duckduckgo_search_tool(
    duckduckgo_client: DDGS | None = None, max_results: int | None = None
) -> Tool[SearchAgentDeps]:
    """Creates a DuckDuckGo search tool.

    Args:
        duckduckgo_client: The DuckDuckGo search client.
        max_results: The maximum number of results. If None, returns results only from the first response.
    """
    return Tool(
        DuckDuckGoSearchTool(
            client=duckduckgo_client or DDGS(), max_results=max_results
        ).__call__,
        name="duckduckgo_search",
        description="Searches DuckDuckGo for the given query and returns the results.",
    )


class SearchAgentOutput(BaseModel):
    """respond with relevant context found from the web searches you have made, the query, and also relevant links that were found. If you encounter errors searching, please respond with whatever context you have found thus far and explain that you need some time before you can search again."""

    relevant_context: str = Field(
        description="A good summary of the most relevant context found from your searches. Ensure to include critical documentation when you find it."
    )
    query: str = Field(description="The query that was made to get the context")
    relevant_links: list[str] = Field(
        description="Links to other URLs that may be relevant"
    )


search_agent: Agent[SearchAgentDeps, SearchAgentOutput] = Agent(
    model=get_pydantic_ai_model_by_model_name(cli_settings.WEB_SEARCH_AGENT_MODEL_NAME),
    deps_type=SearchAgentDeps,
    tools=[
        sequential_thinking,
        duckduckgo_search_tool(max_results=3),
    ],
    output_type=SearchAgentOutput,
    retries=5,
    output_retries=5,
)


@search_agent.system_prompt
def system_prompt(ctx: RunContext[SearchAgentDeps]) -> str:
    return process_template("search_system.jinja", {})


@with_progress_display_async("web_search", "Searching the web")
async def web_search(
    ctx: RunContext[SearchAgentDeps], prompt: str
) -> SearchAgentOutput:
    """
    Search the web for documentation.

    Here is an intent description that may contain urls:
        <INTENT></INTENT>

    IMPORTANT: useful for searching through the web for documentation, api definitions, etc.

    <Example Prompt>
        I need to know about the ast-grep documentation so that I can understand how to use it lint a repo.
    </Example Prompt>

    Args:
        ctx: The run context containing dependencies.
        prompt: The prompt to send to the search agent.

    Returns:
        The relevant context retrieved from the web search and the query that was made, and relevant links.
    """
    logger.info(safe_str_for_log(f"Search Agent Prompt: {prompt}"))
    result = await search_agent.run(
        process_template(
            "search.jinja",
            {
                "prompt": prompt,
            },
        ),
        deps=ctx.deps,
        model_settings=get_model_settings_by_model_name(
            cli_settings.WEB_SEARCH_AGENT_MODEL_NAME
        ),
    )
    output = result.output
    usage = result.usage()

    logger.info(safe_str_for_log(f"Search query: {output.query}"))
    logger.info(safe_str_for_log(f"Search usage: {usage}"))
    return output
