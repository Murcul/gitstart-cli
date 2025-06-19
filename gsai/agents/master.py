"""Master agent for CLI that delegates tasks to specialized agents."""

from typing import Annotated

import git
from annotated_types import MinLen
from loguru import logger
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, Tool, capture_run_messages
from pydantic_ai.messages import ModelMessage
from pydantic_ai.usage import UsageLimits

from gsai.agents.code_writing import (
    CodeWritingAgentDeps,
    CodeWritingAgentOutput,
    code_writing_agent,
)
from gsai.agents.git_operations import (
    GitOperationsAgentDeps,
    GitOperationsAgentOutput,
    git_operations_agent,
)
from gsai.agents.implementation_planning import (
    ImplementationPlanningAgentDeps,
    ImplementationPlanningAgentOutput,
    implementation_planning_agent,
)
from gsai.agents.models import (
    get_model_settings_by_model_name,
    get_pydantic_ai_model_by_model_name,
)
from gsai.agents.prompts.helpers import process_template
from gsai.agents.question_answering import (
    QuestionAnsweringAgentDeps,
    QuestionAnsweringAgentOutput,
    question_answering_agent,
)
from gsai.agents.research import ResearchAgentDeps, ResearchAgentOutput, research_agent
from gsai.agents.ticket_writing import (
    TicketWritingAgentDeps,
    TicketWritingAgentOutput,
    ticket_writing_agent,
)
from gsai.agents.tools import sequential_thinking
from gsai.agents.tools.deps import CodebaseDeps

# from ai_cli.agents.tools import sequential_thinking
from gsai.agents.tools.save_to_memory import save_to_memory
from gsai.config import cli_settings
from gsai.display_helpers import get_current_display, with_progress_display_async


class MasterAgentOutput(BaseModel):
    """Output from the master agent with task delegation results."""

    response: Annotated[str, MinLen(1)] = Field(
        description="The final response back to the user"
    )
    files_modified: list[str] = Field(
        default_factory=list,
        description="List of files that were modified (for code writing tasks)",
    )
    files_created: list[str] = Field(
        default_factory=list,
        description="List of files that were created (for code writing tasks)",
    )
    git_operations: list[str] = Field(
        default_factory=list, description="List of git operations that were performed"
    )
    conversation_title: str = Field(
        default="GitStart AI Session", description="A short title for this conversation"
    )


class MasterAgentDeps(CodebaseDeps):
    """Dependencies for the master agent."""

    message_history: list[ModelMessage]


@with_progress_display_async(
    "delegate_to_code_writing_agent", "Writing code...", is_agentic_tool=True
)
async def delegate_to_code_writing_agent(
    ctx: RunContext[MasterAgentDeps],
) -> CodeWritingAgentOutput:
    """Delegates code writing tasks to the specialized code writing agent. This should be used for implementing features, fixing bugs, or modifying code.

    The code writing agent will implement the requested changes based on the information provided. Without sufficient context, the agent may produce incorrect or incomplete code.
    """
    logger.info("delegating to Code Writing")

    # Import here to avoid circular imports
    deps = CodeWritingAgentDeps(
        repo_path=ctx.deps.repo_path,
        security_context=ctx.deps.security_context,
        approval_manager=ctx.deps.approval_manager,
        cache=ctx.deps.cache,
        thought_history=ctx.deps.thought_history,
        branches=ctx.deps.branches,
        session_state=ctx.deps.session_state,
    )

    messages = ctx.messages[0:-1]
    logger.info(messages)
    captured_messages: list[ModelMessage] = []
    try:
        with capture_run_messages() as captured_messages:
            result = await code_writing_agent.run(
                "Given the message history above, perform your instructions",
                deps=deps,
                message_history=messages,
                usage_limits=UsageLimits(request_limit=100),
                model_settings=get_model_settings_by_model_name(
                    cli_settings.CODING_AGENT_MODEL_NAME
                ),
            )

            # Note: Code writing agent doesn't have markdown content to display
            # The summary is already shown in the completion message

            return result.output
        logger.info(captured_messages)
    except Exception:
        logger.info(captured_messages)
        raise


@with_progress_display_async(
    "delegate_to_question_answering_agent",
    "Researching answer...",
    is_agentic_tool=True,
)
async def delegate_to_question_answering_agent(
    ctx: RunContext[MasterAgentDeps],
) -> QuestionAnsweringAgentOutput:
    """Delegates Q&A tasks to the specialized question answering agent. This should be used for answering user questions about code, concepts, technologies, or development practices.

    The question answering agent will research and respond to the query based on the provided context. Incomplete context may result in generic or inaccurate answers.
    """
    logger.info("delegating to Q&A")

    # Import here to avoid circular imports

    deps = QuestionAnsweringAgentDeps(
        repo_path=ctx.deps.repo_path,
        security_context=ctx.deps.security_context,
        approval_manager=ctx.deps.approval_manager,
        cache=ctx.deps.cache,
        thought_history=ctx.deps.thought_history,
        branches=ctx.deps.branches,
        session_state=ctx.deps.session_state,
    )

    messages = ctx.messages[0:-1]
    logger.info(messages)
    result = await question_answering_agent.run(
        "Given the message history above, perform your instructions",
        deps=deps,
        message_history=messages,
        usage_limits=UsageLimits(request_limit=100),
        model_settings=get_model_settings_by_model_name(
            cli_settings.QUESTION_ANSWERING_AGENT_MODEL_NAME
        ),
    )

    # Note: Question answering agent doesn't have markdown content to display
    # The response is already shown in the main chat flow

    return result.output


@with_progress_display_async(
    "delegate_to_git_operations_agent",
    "Performing git operations...",
    is_agentic_tool=True,
)
async def delegate_to_git_operations_agent(
    ctx: RunContext[MasterAgentDeps],
) -> GitOperationsAgentOutput:
    """Delegates git operations to the specialized git operations agent. This should be used for managing version control tasks such as creating branches, committing changes, handling merge conflicts, or other git-related operations.

    The git operations agent will perform the requested version control tasks based on the information provided. Insufficient context may lead to improper git operations or workflow violations.
    """
    logger.info("delegating to Git Ops")

    # Import here to avoid circular imports

    deps = GitOperationsAgentDeps(
        repo_path=ctx.deps.repo_path,
        security_context=ctx.deps.security_context,
        approval_manager=ctx.deps.approval_manager,
        cache=ctx.deps.cache,
        thought_history=ctx.deps.thought_history,
        branches=ctx.deps.branches,
        git_repo=git.Repo(ctx.deps.repo_path, search_parent_directories=True),
        session_state=ctx.deps.session_state,
    )

    messages = ctx.messages[0:-1]
    logger.info(messages)
    result = await git_operations_agent.run(
        "Given the message history above, perform your instructions",
        deps=deps,
        message_history=messages,
        usage_limits=UsageLimits(request_limit=100),
        model_settings=get_model_settings_by_model_name(
            cli_settings.GIT_OPERATIONS_AGENT_MODEL_NAME
        ),
    )

    # Note: Git operations agent doesn't have markdown content to display
    # The operations are already shown in the completion message

    return result.output


@with_progress_display_async(
    "delegate_to_implementation_planning_agent",
    "Creating implementation plan...",
    is_agentic_tool=True,
)
async def delegate_to_implementation_planning_agent(
    ctx: RunContext[MasterAgentDeps],
) -> ImplementationPlanningAgentOutput:
    """Delegates implementation planning to the specialized planning agent. This should be used before code writing to create a detailed technical plan for implementing features, fixing bugs, or making architectural changes.

    The implementation planning agent will create a detailed technical plan including file changes, architectural approaches, algorithm selections, and potential challenges. This plan should be used as input when subsequently delegating to the code writing agent. Incomplete context may result in plans that don't align with project requirements or architecture.
    """
    logger.info("delegating to Implementation Planning")

    # Import here to avoid circular imports

    deps = ImplementationPlanningAgentDeps(
        repo_path=ctx.deps.repo_path,
        security_context=ctx.deps.security_context,
        approval_manager=ctx.deps.approval_manager,
        cache=ctx.deps.cache,
        thought_history=ctx.deps.thought_history,
        branches=ctx.deps.branches,
        session_state=ctx.deps.session_state,
    )

    messages = ctx.messages[0:-1]
    logger.info(messages)
    result = await implementation_planning_agent.run(
        "Given the message history above, perform your instructions",
        deps=deps,
        message_history=messages,
        usage_limits=UsageLimits(request_limit=100),
        model_settings=get_model_settings_by_model_name(
            cli_settings.IMPLEMENTATION_PLAN_AGENT_MODEL_NAME
        ),
    )

    if result.output and (display := get_current_display()):
        display.show_markdown_result(result.output, "implementation_plan")

    return result.output


@with_progress_display_async(
    "delegate_to_research_agent", "Conducting research...", is_agentic_tool=True
)
async def delegate_to_research_agent(
    ctx: RunContext[MasterAgentDeps],
) -> ResearchAgentOutput:
    """Delegates research tasks to the specialized research agent. This should be used for gathering information, exploring technologies, investigating solutions, or analyzing code patterns.

    The research agent will conduct the investigation based on the information provided and return comprehensive findings. Insufficient context may lead to research that misses critical considerations or produces tangential results.
    """
    logger.info("delegating to research")

    # Import here to avoid circular imports

    deps = ResearchAgentDeps(
        repo_path=ctx.deps.repo_path,
        security_context=ctx.deps.security_context,
        approval_manager=ctx.deps.approval_manager,
        cache=ctx.deps.cache,
        thought_history=ctx.deps.thought_history,
        branches=ctx.deps.branches,
        session_state=ctx.deps.session_state,
    )

    messages = ctx.messages[0:-1]
    logger.info(messages)
    result = await research_agent.run(
        "Given the message history above, perform your instructions",
        deps=deps,
        message_history=messages,
        usage_limits=UsageLimits(request_limit=100),
        model_settings=get_model_settings_by_model_name(
            cli_settings.RESEARCH_AGENT_MODEL_NAME
        ),
    )

    if result.output and (display := get_current_display()):
        display.show_markdown_result(result.output, "research")

    return result.output


@with_progress_display_async(
    "delegate_to_ticket_writing_agent", "Writing ticket...", is_agentic_tool=True
)
async def delegate_to_ticket_writing_agent(
    ctx: RunContext[MasterAgentDeps],
) -> TicketWritingAgentOutput:
    """Delegate ticket_writing to the specialized ticket_writing agent."""
    logger.info("delegating to ticket_writing")

    # Import here to avoid circular imports

    deps = TicketWritingAgentDeps(
        repo_path=ctx.deps.repo_path,
        security_context=ctx.deps.security_context,
        approval_manager=ctx.deps.approval_manager,
        cache=ctx.deps.cache,
        thought_history=ctx.deps.thought_history,
        branches=ctx.deps.branches,
        session_state=ctx.deps.session_state,
    )

    messages = ctx.messages[0:-1]
    logger.info(messages)
    result = await ticket_writing_agent.run(
        "Given the message history above, perform your instructions",
        deps=deps,
        message_history=messages,
        usage_limits=UsageLimits(request_limit=100),
        model_settings=get_model_settings_by_model_name(
            cli_settings.TICKET_WRITING_AGENT_MODEL_NAME
        ),
    )

    if result.output and (display := get_current_display()):
        display.show_markdown_result(result.output, "ticket")

    return result.output


master_agent: Agent[MasterAgentDeps, MasterAgentOutput] = Agent(
    model=get_pydantic_ai_model_by_model_name(cli_settings.CLI_MASTER_AGENT_MODEL_NAME),
    deps_type=MasterAgentDeps,
    tools=[
        # sequential_thinking,
        Tool(save_to_memory, takes_ctx=True),
        Tool(delegate_to_code_writing_agent, takes_ctx=True),
        Tool(delegate_to_question_answering_agent, takes_ctx=True),
        Tool(delegate_to_git_operations_agent, takes_ctx=True),
        Tool(delegate_to_implementation_planning_agent, takes_ctx=True),
        Tool(delegate_to_research_agent, takes_ctx=True),
        Tool(delegate_to_ticket_writing_agent, takes_ctx=True),
        sequential_thinking,
    ],
    output_type=MasterAgentOutput,
    retries=5,
    output_retries=5,
)


@master_agent.instructions
def master_agent_instructions(ctx: RunContext[MasterAgentDeps]) -> str:
    return process_template("master_instructions.jinja", {"ctx": ctx})


@master_agent.system_prompt
def shared_context(ctx: RunContext[MasterAgentDeps]) -> str:
    return process_template("shared_context.jinja", {"ctx": ctx})
