"""
Tool definitions (JSON schemas) for OpenAI function calling.
These schemas are automatically generated from the @tool decorator in actions.py.
Import actions module to ensure all tools are registered.
"""

# Import tool definitions from decorator
from app.agent.tools.decorator import get_tool_definitions

# Get tool definitions (automatically generated from @tool decorators)
TOOL_DEFINITIONS = get_tool_definitions()

