"""
Agent Zero: A lightweight, modular AI agent framework.

Provides core task planning, execution, and memory management
for building autonomous AI agents.
"""

from .core import Agent
from .config import AgentConfig, config

__version__ = "0.1.0"
__all__ = ["Agent", "AgentConfig", "config"]
