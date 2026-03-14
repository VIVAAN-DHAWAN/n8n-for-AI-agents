"""
Configuration management for Agent Zero.

Handles env vars, API keys, and agent behavior settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file if present
load_dotenv()


class AgentSettings(BaseSettings):
    """Pydantic-based configuration with env var support."""
    
    model_config = SettingsConfigDict(
        env_prefix="AGENT_ZERO_",
        env_file=".env",
        extra="ignore",
    )
    
    # LLM Configuration
    api_key: Optional[str] = Field(default=None, alias="AGENT_ZERO_API_KEY")
    model: str = Field(default="gpt-4o", alias="AGENT_ZERO_MODEL")
    base_url: Optional[str] = Field(default=None, alias="AGENT_ZERO_BASE_URL")
    
    # Agent Behavior
    max_retries: int = Field(default=3, alias="AGENT_ZERO_MAX_RETRIES")
    timeout: int = Field(default=60, alias="AGENT_ZERO_TIMEOUT")
    max_steps: int = Field(default=10, alias="AGENT_ZERO_MAX_STEPS")
    
    # Memory Settings
    memory_path: str = Field(default="./memory", alias="AGENT_ZERO_MEMORY_PATH")
    memory_max_tokens: int = Field(default=4000, alias="AGENT_ZERO_MEMORY_MAX_TOKENS")
    
    # Debug
    debug: bool = Field(default=False, alias="AGENT_ZERO_DEBUG")
    verbose: bool = Field(default=True, alias="AGENT_ZERO_VERBOSE")


class AgentConfig:
    """Simple config accessor with sensible defaults."""
    
    def __init__(self, **overrides):
        self._settings = AgentSettings(**overrides)
    
    @property
    def settings(self) -> AgentSettings:
        return self._settings
    
    # LLM
    @property
    def api_key(self) -> Optional[str]:
        return self._settings.api_key
    
    @property
    def model(self) -> str:
        return self._settings.model
    
    @property
    def base_url(self) -> Optional[str]:
        return self._settings.base_url
    
    # Behavior
    @property
    def max_retries(self) -> int:
        return self._settings.max_retries
    
    @property
    def timeout(self) -> int:
        return self._settings.timeout
    
    @property
    def max_steps(self) -> int:
        return self._settings.max_steps
    
    # Memory
    @property
    def memory_path(self) -> str:
        return self._settings.memory_path
    
    @property
    def memory_max_tokens(self) -> int:
        return self._settings.memory_max_tokens
    
    # Debug
    @property
    def debug(self) -> bool:
        return self._settings.debug
    
    @property
    def verbose(self) -> bool:
        return self._settings.verbose
    
    def update(self, **kwargs) -> "AgentConfig":
        """Create a new config with updated values (immutable)."""
        current = self._settings.model_dump()
        current.update(kwargs)
        return AgentConfig(**current)


# Global default config instance
config = AgentConfig()
