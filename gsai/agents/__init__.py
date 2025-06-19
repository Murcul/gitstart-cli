"""CLI-specific agents with security and approval workflows."""

from gsai.agents.master import MasterAgentDeps, MasterAgentOutput, master_agent

__all__ = [
    "master_agent",
    "MasterAgentDeps",
    "MasterAgentOutput",
]
