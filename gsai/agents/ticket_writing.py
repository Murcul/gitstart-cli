from typing import Annotated

from annotated_types import MinLen
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, Tool

from gsai.agents.models import get_pydantic_ai_model_by_model_name
from gsai.agents.prompts.helpers import process_template
from gsai.agents.tools import (
    CodebaseDeps,
    search_for_code,
    search_for_files,
    sequential_thinking,
    view_file,
)
from gsai.agents.tools_agentic.expert import expert
from gsai.agents.tools_agentic.web_navigation import web_navigation
from gsai.config import cli_settings


class TicketWritingAgentOutput(BaseModel):
    """respond with a response for the user and a ticket title and a ticket description"""

    response: Annotated[str, MinLen(1)] = Field(
        description="A response to the user, minimize tokens, be to the point, and try to ask one question at a time. Use Markdown format as it will need to be read by the user."
    )
    ticket_title: str | None = Field(
        description="The Title for the ticket you propose to the user if you are ready to do so, if you have questions don't propose a ticket. Use Markdown format as it will need to be read by the user."
    )
    ticket_description: str | None = Field(
        description="The description for the ticket you propose to the user if you are ready to do so, if you have questions don't propose a ticket. Use Markdown format as it will need to be read by the user."
    )
    conversation_title_summary: str = Field(
        description="A very short, concise summary of what this conversation is about. should be less than 6 words as it will be used as the title of the conversation."
    )


class TicketWritingAgentDeps(CodebaseDeps):
    pass


ticket_writing_agent: Agent[TicketWritingAgentDeps, TicketWritingAgentOutput] = Agent(
    model=get_pydantic_ai_model_by_model_name(
        cli_settings.TICKET_WRITING_AGENT_MODEL_NAME
    ),
    deps_type=TicketWritingAgentDeps,
    tools=[
        sequential_thinking,
        search_for_code,
        search_for_files,
        view_file,
        Tool(web_navigation, takes_ctx=True),
        Tool(expert, takes_ctx=True),
    ],
    output_type=TicketWritingAgentOutput,
    retries=5,
    output_retries=5,
)


@ticket_writing_agent.instructions
def instructions(ctx: RunContext[TicketWritingAgentDeps]) -> str:
    return process_template(
        "ticket_writing_system.jinja",
        {"ctx": ctx},
    )
