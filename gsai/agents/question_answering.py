"""CLI-specific question answering agent with security validation."""

from typing import Annotated

from annotated_types import MinLen
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, Tool

from gsai.agents.models import get_pydantic_ai_model_by_model_name
from gsai.agents.tools import (  # search_codebase_natural_language,
    list_files,
    quick_view_file,
    save_to_memory,
    search_for_code,
    search_for_files,
    view_file,
)
from gsai.agents.tools.deps import CodebaseDeps
from gsai.agents.tools_agentic.expert import expert
from gsai.agents.tools_agentic.web_navigation import web_navigation
from gsai.config import cli_settings


class QuestionAnsweringAgentOutput(BaseModel):
    """respond with a response for the user a short answer and a conversation title summary"""

    response: Annotated[str, MinLen(1)] = Field(
        description="A detailed response to the user's question using Markdown format"
    )
    short_answer: str = Field(description="A one-line answer to the question")
    conversation_title_summary: str = Field(
        description="A very short, concise summary of what this conversation is about (less than 6 words)"
    )


class QuestionAnsweringAgentDeps(CodebaseDeps):
    """Dependencies for the CLI question answering agent."""

    pass


question_answering_agent: Agent[
    QuestionAnsweringAgentDeps, QuestionAnsweringAgentOutput
] = Agent(
    model=get_pydantic_ai_model_by_model_name(
        cli_settings.TICKET_WRITING_AGENT_MODEL_NAME
    ),
    deps_type=QuestionAnsweringAgentDeps,
    tools=[
        # search_codebase_natural_language,
        search_for_code,
        view_file,
        quick_view_file,
        list_files,
        search_for_files,
        # sequential_thinking,
        Tool(expert, takes_ctx=True),
        Tool(web_navigation, takes_ctx=True),
        Tool(save_to_memory, takes_ctx=True),
    ],
    output_type=QuestionAnsweringAgentOutput,
    retries=5,
    output_retries=5,
)


@question_answering_agent.instructions
def question_answering_system_prompt(
    ctx: RunContext[QuestionAnsweringAgentDeps],
) -> str:
    web_search_status = (
        "enabled" if ctx.deps.security_context.web_search_enabled else "disabled"
    )

    return f"""You are an expert software development consultant working in a secure CLI environment. Your role is to answer questions about codebases, programming concepts, and development practices.

## Environment Information:
- Working Directory: {ctx.deps.security_context.working_directory}
- Repository Path: {ctx.deps.repo_path}
- Web Search: {web_search_status}

## Security Constraints:
- All file access is restricted to the working directory
- You can only read files, not modify them
- Web search is {web_search_status}

## Your Capabilities:
1. **Codebase Analysis**: Search and analyze code using natural language queries
2. **Code Understanding**: Explain how code works, its purpose, and architecture
3. **Best Practices**: Provide guidance on coding standards and practices
4. **Documentation**: Help understand and explain documentation
5. **Troubleshooting**: Help diagnose issues and suggest solutions

## Question Types You Handle:
- **Code Explanation**: "How does this function work?"
- **Architecture Questions**: "What is the structure of this project?"
- **Usage Questions**: "How do I use this library/framework?"
- **Best Practices**: "What's the best way to implement X?"
- **Debugging Help**: "Why isn't this code working?"
- **Documentation**: "What does this configuration do?"

## Guidelines:
1. **Thorough Analysis**: Use available tools to thoroughly understand the codebase
2. **Clear Explanations**: Provide clear, well-structured explanations
3. **Context Aware**: Consider the specific codebase and its patterns
4. **Practical Advice**: Give actionable, practical guidance
5. **Security Conscious**: Respect the security constraints

## Response Format:
- Use Markdown formatting for better readability
- Include code examples when helpful
- Provide both detailed explanations and concise summaries
- Structure responses with clear headings and sections

Remember: You are a knowledgeable consultant helping developers understand their codebase and improve their development practices."""
