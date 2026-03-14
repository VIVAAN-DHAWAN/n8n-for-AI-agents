<div align="center">
  <h1>⚡️ Agent Zero Core</h1>
  <p><strong>A minimal, pluggable, and high-performance AI agent framework. Think "n8n for AI agents."</strong></p>
</div>

## 🚀 What is Agent Zero?

Agent Zero is a lightweight, highly extensible framework designed to build, run, and scale AI agents. Instead of bloated frameworks, Agent Zero gives you the raw engine to orchestrate tasks, manage memory, and plug in custom tools seamlessly. It is designed to be the foundational layer for any automated workflow or agentic system.

Whether you're building automated content generators, research assistants, or complex multi-step workflows, Agent Zero provides the scaffolding you need without getting in your way.

## ✨ Features

- **🧠 Core Engine:** Built-in task planning, step execution, and memory management.
- **🔌 Pluggable Architecture:** Easily add custom tools and plugins. If you can write a Python function, you can make an Agent Zero tool.
- **⚡️ Lightweight & Fast:** Minimal dependencies. Focuses on speed and reliability.
- **🛠 Built-in Tooling:** Comes out of the box with file operations, web fetching, and shell execution capabilities.
- **🔄 Async Ready:** Built for modern Python with asynchronous execution in mind.

## 📦 Installation

Clone the repository and install the minimal requirements:

```bash
git clone https://github.com/VIVAAN-DHAWAN/n8n-for-AI-agents.git
cd n8n-for-AI-agents
pip install -r requirements.txt
```

## 🛠 Quick Start

Here is how simple it is to initialize an agent and run a task:

```python
from agent_zero.core import AgentZero
from agent_zero.config import Config

# Initialize the agent
agent = AgentZero(config=Config())

# Run a task
result = agent.run("Research the latest advancements in AI text-to-video models and summarize them.")
print(result)
```

## 🧩 Building Custom Tools

Creating a new tool for Agent Zero is straightforward. Just inherit from the base class and define your functionality:

```python
from agent_zero.tools.base import BaseTool

class MyCustomTool(BaseTool):
    name = "custom_tool"
    description = "Does something awesome."

    def execute(self, **kwargs):
        # Your logic here
        return "Success!"
```

## 🤝 Contributing

We welcome contributions! If you want to add a new tool, improve the core engine, or fix a bug, feel free to open a Pull Request. Let's build the ultimate agent framework together.

## 📄 License

This project is licensed under the MIT License.
