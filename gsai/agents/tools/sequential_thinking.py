"""Sequential thinking tool for AI Coding CLI."""

from loguru import logger
from pydantic_ai import RunContext

from gsai.agents.tools.deps import CodebaseDeps, ThoughtData


def sequential_thinking(
    ctx: RunContext[CodebaseDeps],
    thought: str,
    next_thought_needed: bool,
    thought_number: int,
    total_thoughts: int,
    is_revision: bool | None,
    revises_thought: int | None,
    branch_from_thought: int | None,
    branch_id: str | None,
    needs_more_thoughts: bool | None,
) -> dict[str, str | int | list[str]]:
    """
    A detailed tool for dynamic and reflective problem-solving through thoughts.
    This tool helps analyze problems through a flexible thinking process that can adapt and evolve.
    Each thought can build on, question, or revise previous insights as understanding deepens.

    When to use this tool:
    - Breaking down complex problems into steps
    - Planning and design with room for revision
    - Analysis that might need course correction
    - Problems where the full scope might not be clear initially
    - Problems that require a multi-step solution
    - Tasks that need to maintain context over multiple steps
    - Situations where irrelevant information needs to be filtered out

    Key features:
    - You can adjust total_thoughts up or down as you progress
    - You can question or revise previous thoughts
    - You can add more thoughts even after reaching what seemed like the end
    - You can express uncertainty and explore alternative approaches
    - Not every thought needs to build linearly - you can branch or backtrack
    - Generates a solution hypothesis
    - Verifies the hypothesis based on the Chain of Thought steps
    - Repeats the process until satisfied
    - Provides a correct answer

    Parameters explained:
    - thought: Your current thinking step, which can include:
    * Regular analytical steps
    * Revisions of previous thoughts
    * Questions about previous decisions
    * Realizations about needing more analysis
    * Changes in approach
    * Hypothesis generation
    * Hypothesis verification
    - next_thought_needed: True if you need more thinking, even if at what seemed like the end
    - thought_number: Current number in sequence (can go beyond initial total if needed)
    - total_thoughts: Current estimate of thoughts needed (can be adjusted up/down)
    - is_revision: A boolean indicating if this thought revises previous thinking
    - revises_thought: If is_revision is true, which thought number is being reconsidered
    - branch_from_thought: If branching, which thought number is the branching point
    - branch_id: Identifier for the current branch (if any)
    - needs_more_thoughts: If reaching end but realizing more thoughts needed

    You should:
    1. Start with an initial estimate of needed thoughts, but be ready to adjust
    2. Feel free to question or revise previous thoughts
    3. Don't hesitate to add more thoughts if needed, even at the "end"
    4. Express uncertainty when present
    5. Mark thoughts that revise previous thinking or branch into new paths
    6. Ignore information that is irrelevant to the current step
    7. Generate a solution hypothesis when appropriate
    8. Verify the hypothesis based on the Chain of Thought steps
    9. Repeat the process until satisfied with the solution
    10. Provide a single, ideally correct answer as the final output
    11. Only set next_thought_needed to false when truly done and a satisfactory answer is reached

    :param thought: Your current thinking step.
    :type thought: str
    :param next_thought_needed: Whether another thought step is needed
    :type next_thought_needed: bool
    :param thought_number: Current thought number
    :type thought_number: int minimum 1
    :param total_thoughts: Estimated total thoughts needed
    :type total_thoughts: int minimum 1
    :param is_revision: Whether this revises previous thinking
    :type is_revision: bool optional
    :param revises_thought: Which thought is being reconsidered
    :type revises_thought: int optional minimum 1
    :param branch_from_thought: Branching point thought number
    :type branch_from_thought: int optional minimum 1
    :param branch_id: Branch identifier
    :type branch_id: str optional
    :param needs_more_thoughts: If more thoughts are needed
    :type needs_more_thoughts: bool optional
    :returns: An empty string.
    :rtype: str
    """
    if thought_number > total_thoughts:
        total_thoughts = thought_number

    input_thought = ThoughtData(
        thought=thought,
        next_thought_needed=next_thought_needed,
        thought_number=thought_number,
        total_thoughts=total_thoughts,
        is_revision=is_revision,
        revises_thought=revises_thought,
        branch_from_thought=branch_from_thought,
        branch_id=branch_id,
        needs_more_thoughts=needs_more_thoughts,
    )
    logger.info("Had a thought")

    ctx.deps.thought_history.append(input_thought)
    if branch_from_thought and branch_id:
        branch = ctx.deps.branches.get(branch_id, [])
        branch.append(input_thought)
        ctx.deps.branches[branch_id] = branch

    result: dict[str, str | int | list[str]] = {
        "thought_number": thought_number,
        "total_thoughts": total_thoughts,
        "next_thought_needed": next_thought_needed,
        "branches": list(ctx.deps.branches.keys()),
        "thought_history_length": len(ctx.deps.thought_history),
    }

    return result
