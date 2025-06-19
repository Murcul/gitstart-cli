import httpx
import tiktoken
from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, Tool

from gsai.agents.models import (
    get_model_settings_by_model_name,
    get_pydantic_ai_model_by_model_name,
)
from gsai.agents.prompts.helpers import process_template
from gsai.agents.tools import ThinkingDeps, sequential_thinking
from gsai.config import cli_settings
from gsai.display_helpers import with_progress_display_async
from gsai.utils import safe_str_for_log


class ExtractContextFromURLOutput(BaseModel):
    """respond with A concise summary of the most relevant context found from the URL and a the url that was processed and links found"""

    relevant_context: str = Field(
        description="A concise summary of the most relevant context found from the URLs"
    )
    url_processed: str = Field(description="The URL that was processed")
    relevant_links: list[str] = Field(
        description="Links to other URLs that may be relevant"
    )


class ExtractContextFromURLDeps(ThinkingDeps):
    pass


def extract_content_and_links(soup: BeautifulSoup) -> tuple[str, list[str]]:
    """
    Extract important text content and all links from a page to minimize token usage by an LLM.

    Args:
        soup: BeautifulSoup object representing the parsed HTML

    Returns:
        Tuple containing:
            - A string of important text content with minimal formatting
            - A list of dictionaries containing link information (text and href)
    """
    # Important content is typically in these tags
    content_tags = [
        "p",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "li",
        "td",
        "th",
        "blockquote",
        "pre",
    ]

    # Container tags that typically hold important content
    priority_containers = ["main", "article", "section"]

    # Tags to ignore as they typically contain less relevant content
    ignore_tags = ["script", "style", "noscript", "header", "footer", "nav", "aside"]

    # Extract all links
    links: list[str] = []
    for a in soup.find_all("a"):
        # Ensure we're working with a Tag, not just any PageElement
        if isinstance(a, Tag):
            # Check if href attribute exists and has a value
            if "href" in a.attrs and a.attrs["href"]:
                href = a.get("href", "")
                if isinstance(href, str):
                    href = href.strip()
                else:
                    href = str(href).strip()
                if href and not href.startswith(("#", "javascript:")):
                    text = a.get_text(strip=True)
                    links.append(f"{text}: {href}")

    # Extract important text content
    content: list[str] = []

    def extract_text_from_tag(tag: Tag) -> None:
        if tag.name in ignore_tags:
            return

        if tag.name in content_tags:
            text = tag.get_text(strip=True)
            if text:
                # Add appropriate formatting based on tag type
                if tag.name.startswith("h"):
                    # Add formatting for headers
                    content.append(f"# {text}")
                elif tag.name == "li":
                    content.append(f"• {text}")
                else:
                    content.append(text)

        # Process child tags
        for child in tag.children:
            if isinstance(child, Tag):
                extract_text_from_tag(child)

    # First look for priority containers (main, article, section)
    priority_found = False
    for container_tag in priority_containers:
        containers = soup.find_all(container_tag)
        if containers:
            priority_found = True
            for container in containers:
                if isinstance(container, Tag):
                    extract_text_from_tag(container)

    # If no priority containers were found, fall back to the body
    if not priority_found:
        body_tag = soup.body
        if body_tag:
            for child in body_tag.children:
                if isinstance(child, Tag):
                    extract_text_from_tag(child)
        else:
            # If no body tag found, process from soup
            for child in soup.children:
                if isinstance(child, Tag):
                    extract_text_from_tag(child)

    # Join content with newlines for readability
    full_content = "\n".join(content)
    return full_content, links


async def extract_context_from_url(
    ctx: RunContext[ExtractContextFromURLDeps], url: str
) -> tuple[str, list[str]]:
    """
    Retrieves content from a URL and returns it.

    :param url: The URL to retrieve content from
    :type url: str
    :returns: The content retrieved from the URL
    :rtype: str
    """
    logger.info(safe_str_for_log(f"retrieving info from: {url}"))

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10, follow_redirects=True)

        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()
        if "html" not in content_type:
            return response.text, []
        # Parse HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract important content and links
        content, links = extract_content_and_links(soup)
        encoding = tiktoken.get_encoding("o200k_base")
        input_token_count = len(encoding.encode(content + str(links)))
        logger.info(safe_str_for_log(f"url token count: {input_token_count}"))
        if input_token_count > 100000:
            return (
                "The content of this was too huge I'm only including the links",
                links,
            )

        # If no content was extracted, fall back to returning a message
        if not content:
            logger.warning(
                safe_str_for_log(f"No meaningful content extracted from {url}")
            )
            return f"No meaningful content could be extracted from {url}", links
        return content, links
    except Exception as e:
        logger.error(safe_str_for_log(f"Error retrieving URL {url}: {str(e)}"))
        return f"error getting {url}", []


extract_relevant_context_from_url_agent: Agent[
    ExtractContextFromURLDeps, ExtractContextFromURLOutput
] = Agent(
    model=get_pydantic_ai_model_by_model_name(
        cli_settings.EXTRACT_CONTEXT_FROM_URL_AGENT_MODEL_NAME
    ),
    deps_type=ExtractContextFromURLDeps,
    tools=[sequential_thinking, Tool(extract_context_from_url, takes_ctx=True)],
    output_type=ExtractContextFromURLOutput,
    retries=5,
    output_retries=5,
)


@extract_relevant_context_from_url_agent.system_prompt
def system_prompt(ctx: RunContext[ExtractContextFromURLDeps]) -> str:
    return process_template("extract_relevant_context_from_url_system.jinja", {})


@with_progress_display_async(
    "extract_relevant_context_from_url", "Extracting context from URL"
)
async def extract_relevant_context_from_url(
    ctx: RunContext[ExtractContextFromURLDeps], prompt: str
) -> ExtractContextFromURLOutput:
    """
    Identify a single URL in text and extract all relevant context to the text provided.

    IMPORTANT: useful for using links provided by the user and searching through the links for documentation, api definitions, etc.

    <Example Prompt>
        Here is an intent description that may contain urls:
        <INTENT></INTENT>

        Here is a URL to take a look at: https://docs.temporal.com

        Please help me figure out how to do testing when using temporal with python
    </Example Prompt>

    Args:
        ctx: The run context containing dependencies.
        prompt: The prompt to send to the web navigation agent.

    Returns:
        The relevant context retrieved from the URL, url_processed and the list of links found.
    """

    logger.info(safe_str_for_log(f"ExtractContext Agent Prompt: {prompt}"))
    result = await extract_relevant_context_from_url_agent.run(
        process_template(
            "extract_relevant_context_from_url.jinja",
            {
                "prompt": prompt,
            },
        ),
        deps=ctx.deps,
        model_settings=get_model_settings_by_model_name(
            cli_settings.EXTRACT_CONTEXT_FROM_URL_AGENT_MODEL_NAME
        ),
    )
    output = result.output
    usage = result.usage()

    logger.info(safe_str_for_log(f"url processed: {output.url_processed}"))
    logger.info(safe_str_for_log(f"ExtractContextFromURLs usage: {usage}"))
    return output
