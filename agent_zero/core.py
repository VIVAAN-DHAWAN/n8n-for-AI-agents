"""
Agent Zero Core: The main agent class with planning, execution, and memory.
"""

import json
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Type
from pathlib import Path

from .config import AgentConfig, config


class Step:
    """Represents a single step in a task plan."""
    
    def __init__(self, step_id: int, description: str, tool: Optional[str] = None, params: Optional[Dict] = None):
        self.step_id = step_id
        self.description = description
        self.tool = tool
        self.params = params or {}
        self.result: Optional[Any] = None
        self.status: str = "pending"  # pending, running, completed, failed
        self.error: Optional[str] = None
        self.created_at = datetime.now().isoformat()
        self.completed_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "step_id": self.step_id,
            "description": self.description,
            "tool": self.tool,
            "params": self.params,
            "result": self.result,
            "status": self.status,
            "error": self.error,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }
    
    def __repr__(self) -> str:
        return f"Step({self.step_id}: {self.description[:50]}... [{self.status}])"


class Memory:
    """Simple in-memory + file-based storage for agent context."""
    
    def __init__(self, path: str = "./memory", max_tokens: int = 4000):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        self.max_tokens = max_tokens
        self._sessions: Dict[str, List[Dict]] = {}
        self._current_session: List[Dict] = []
    
    def add(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add an entry to current session memory."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
            "metadata": metadata or {},
        }
        self._current_session.append(entry)
        self._trim_if_needed()
    
    def _trim_if_needed(self):
        """Simple trimming based on entry count (approximate token limit)."""
        while len(self._current_session) > 100:  # Rough proxy for token limit
            self._current_session.pop(0)
    
    def get_context(self, last_n: int = 10) -> List[Dict]:
        """Get recent context entries."""
        return self._current_session[-last_n:]
    
    def save_session(self, session_id: str):
        """Persist session to disk."""
        filepath = self.path / f"{session_id}.json"
        self._sessions[session_id] = self._current_session.copy()
        with open(filepath, "w") as f:
            json.dump(self._current_session, f, indent=2)
    
    def load_session(self, session_id: str) -> List[Dict]:
        """Load a session from disk."""
        filepath = self.path / f"{session_id}.json"
        if filepath.exists():
            with open(filepath, "r") as f:
                self._current_session = json.load(f)
                self._sessions[session_id] = self._current_session
                return self._current_session
        return []
    
    def clear(self):
        """Clear current session."""
        self._current_session = []


class ToolRegistry:
    """Registry for available tools/functions."""
    
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
    
    def register(self, name: str, func: Callable):
        """Register a tool by name."""
        self._tools[name] = func
    
    def get(self, name: str) -> Optional[Callable]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())
    
    def execute(self, name: str, **kwargs) -> Any:
        """Execute a tool by name with given params."""
        tool = self.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")
        return tool(**kwargs)


class Agent:
    """
    The core Agent Zero agent.
    
    Features:
    - Task breakdown into steps
    - Step execution with tools
    - Memory persistence
    - Error handling with retries
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
        self.memory = Memory(
            path=self.config.memory_path,
            max_tokens=self.config.memory_max_tokens
        )
        self.tools = ToolRegistry()
        self.steps: List[Step] = []
        self.current_step: Optional[Step] = None
        self._running = False
        
        # Register default tools
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register built-in tools."""
        self.tools.register("wait", lambda seconds=1: time.sleep(seconds) or f"Waited {seconds}s")
        self.tools.register("log", lambda message, level="info": self._log(message, level))
        self.tools.register("get_time", lambda: datetime.now().isoformat())
    
    def _log(self, message: str, level: str = "info") -> str:
        """Internal logging."""
        if self.config.verbose:
            print(f"[{level.upper()}] {message}")
        self.memory.add("system", message, {"level": level})
        return message
    
    # ------------------------------------------------------------------
    # Core Agent Loop
    # ------------------------------------------------------------------
    
    def run(self, task: str, auto_plan: bool = True) -> Dict[str, Any]:
        """
        Execute a task end-to-end.
        
        Args:
            task: The task description
            auto_plan: If True, generates a plan automatically
        
        Returns:
            Execution result dict with status, steps, and output
        """
        self._log(f"Starting task: {task}", "info")
        self.memory.add("user", task)
        
        # Generate or use existing plan
        if auto_plan:
            self.steps = self.create_plan(task)
        
        if not self.steps:
            return {"status": "error", "error": "No steps generated", "steps": []}
        
        # Execute steps
        self._running = True
        results = []
        
        for step in self.steps:
            if not self._running:
                break
            
            result = self.execute_step(step)
            results.append(result)
            
            if result.get("status") == "failed" and not self.config.max_retries:
                break
        
        # Final summary
        success_count = sum(1 for r in results if r.get("status") == "completed")
        summary = {
            "status": "completed" if success_count == len(self.steps) else "partial",
            "task": task,
            "total_steps": len(self.steps),
            "completed_steps": success_count,
            "results": results,
            "steps": [s.to_dict() for s in self.steps],
        }
        
        self.memory.add("system", f"Task completed with status: {summary['status']}")
        self._log(f"Task finished: {summary['status']}", "info")
        
        return summary
    
    def create_plan(self, task: str) -> List[Step]:
        """
        Break down a task into steps.
        
        In production, this would use an LLM. For now, uses a simple heuristic.
        """
        self._log(f"Creating plan for: {task}", "info")
        