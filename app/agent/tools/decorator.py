"""
Tool decorator for automatic OpenAI schema generation and registration.
This module provides a @tool decorator that automatically generates OpenAI
function schemas and registers tools, making actions.py the single source of truth.
"""

import inspect
from typing import Dict, Any, Callable, Optional, get_type_hints, get_origin, get_args
from functools import wraps


# Central registry for all tools
_TOOL_REGISTRY: Dict[str, Callable] = {}
_TOOL_DEFINITIONS: list[Dict[str, Any]] = []


def _python_type_to_json_type(python_type: type) -> str:
    """Convert Python type to JSON schema type."""
    type_mapping = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }
    
    # Handle generic types like List[str], Dict[str, Any]
    origin = get_origin(python_type)
    if origin is not None:
        if origin is list:
            return "array"
        elif origin is dict:
            return "object"
    
    return type_mapping.get(python_type, "string")


def _extract_type_info(param_type: type) -> Dict[str, Any]:
    """Extract type information for a parameter."""
    type_info = {"type": _python_type_to_json_type(param_type)}
    
    # Handle List types
    origin = get_origin(param_type)
    if origin is list:
        args = get_args(param_type)
        if args:
            item_type = args[0]
            type_info["items"] = {"type": _python_type_to_json_type(item_type)}
    
    return type_info


def _parse_docstring(docstring: Optional[str]) -> Dict[str, str]:
    """
    Parse docstring to extract description and parameter descriptions.
    Expects Google-style docstrings.
    """
    if not docstring:
        return {"description": "", "params": {}}
    
    lines = [line.rstrip() for line in docstring.strip().split('\n')]
    description_lines = []
    params = {}
    in_args_section = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Check for Args section
        if stripped.startswith("Args:") or stripped == "Args:":
            in_args_section = True
            continue
        
        # Check for Returns or Raises sections (end of Args)
        if stripped.startswith(("Returns:", "Raises:")):
            in_args_section = False
            continue
        
        if in_args_section:
            # Parse parameter lines
            # Format: "param_name: Description" or "param_name: Description with details"
            if ':' in stripped:
                parts = stripped.split(':', 1)
                if len(parts) == 2:
                    param_name = parts[0].strip()
                    param_desc = parts[1].strip()
                    params[param_name] = param_desc
        else:
            # Collect description lines (before Args section)
            if stripped:
                description_lines.append(stripped)
    
    description = " ".join(description_lines).strip()
    
    return {"description": description, "params": params}


def _generate_openai_schema(
    func: Callable,
    name: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Generate OpenAI function schema from function signature and docstring."""
    
    # Get function name
    tool_name = name or func.__name__
    
    # Parse docstring
    doc_info = _parse_docstring(func.__doc__)
    tool_description = description or doc_info["description"] or f"Execute {tool_name}"
    
    # Get function signature
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)
    
    # Build parameters schema
    properties = {}
    required = []
    
    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue
        
        # Get type hint
        param_type = type_hints.get(param_name, str)
        
        # Extract type info
        type_info = _extract_type_info(param_type)
        
        # Get description from docstring or use default
        param_description = doc_info["params"].get(param_name, f"{param_name} parameter")
        
        properties[param_name] = {
            **type_info,
            "description": param_description
        }
        
        # Add to required if no default value
        if param.default == inspect.Parameter.empty:
            required.append(param_name)
    
    return {
        "type": "function",
        "function": {
            "name": tool_name,
            "description": tool_description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
    }


def tool(
    func: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None
):
    """
    Decorator to register a function as a tool and generate OpenAI schema.
    
    Args:
        func: Function to decorate (when used as @tool)
        name: Optional custom name for the tool (defaults to function name)
        description: Optional custom description (defaults to docstring)
    
    Usage:
        @tool
        def my_tool(param1: str, param2: int) -> Dict[str, Any]:
            \"\"\"
            Tool description here.
            
            Args:
                param1: Description of param1
                param2: Description of param2
            \"\"\"
            ...
        
        # Or with custom name/description:
        @tool(name="custom_name", description="Custom description")
        def my_tool(...):
            ...
    """
    def decorator(f: Callable) -> Callable:
        # Generate schema
        schema = _generate_openai_schema(f, name=name, description=description)
        tool_name = name or f.__name__
        
        # Register function
        _TOOL_REGISTRY[tool_name] = f
        
        # Register schema
        _TOOL_DEFINITIONS.append(schema)
        
        # Preserve original function metadata
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        
        # Store metadata
        wrapper._tool_name = tool_name
        wrapper._tool_schema = schema
        
        return wrapper
    
    # Support both @tool and @tool() syntax
    if func is None:
        # Called as @tool() with optional args
        return decorator
    else:
        # Called as @tool without parentheses
        return decorator(func)


def get_tool_registry() -> Dict[str, Callable]:
    """Get the tool registry."""
    return _TOOL_REGISTRY.copy()


def get_tool_definitions() -> list[Dict[str, Any]]:
    """Get OpenAI tool definitions."""
    return _TOOL_DEFINITIONS.copy()


def get_tool_function(tool_name: str) -> Callable:
    """
    Get a tool function by name.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        The tool function
        
    Raises:
        KeyError: If tool name is not found in registry
    """
    if tool_name not in _TOOL_REGISTRY:
        raise KeyError(f"Unknown tool: {tool_name}")
    return _TOOL_REGISTRY[tool_name]


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool function with the given arguments.
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Arguments to pass to the tool function
        
    Returns:
        Tool execution result
    """
    tool_func = get_tool_function(tool_name)
    
    try:
        # Get function signature to determine how to call it
        sig = inspect.signature(tool_func)
        params = list(sig.parameters.keys())
        
        # Build arguments dict based on parameter names
        call_args = {}
        for param_name in params:
            if param_name in arguments:
                call_args[param_name] = arguments[param_name]
        
        # Call function with unpacked arguments
        result = tool_func(**call_args)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"Error executing tool {tool_name}: {str(e)}"
        }

