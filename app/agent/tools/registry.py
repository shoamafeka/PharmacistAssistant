"""
Tool registry - Maps function names to Python code (The "Manager").
This module provides a registry that maps tool names to their corresponding
Python function implementations. Tools are automatically registered via @tool decorator.
"""

from typing import Dict, Callable

# Import registry functions from decorator
from app.agent.tools.decorator import (
    get_tool_registry,
    execute_tool,
)

# Get tool registry (automatically populated from @tool decorators)
TOOL_REGISTRY: Dict[str, Callable] = get_tool_registry()

