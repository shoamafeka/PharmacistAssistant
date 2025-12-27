"""
Agent handler for the Pharmacist Assistant.
Handles streaming conversations with OpenAI API and tool calling.
"""

import json
from typing import Dict, List, Any, Optional, Iterator
from openai import OpenAI
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools.definitions import TOOL_DEFINITIONS
from app.agent.tools.registry import execute_tool


class PharmacistAgent:
    """
    Stateless agent handler for pharmacy assistant.
    Maintains conversation context within a session but does not persist between sessions.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-5"):
        """
        Initialize the agent.
        
        Args:
            api_key: OpenAI API key (if None, will use OPENAI_API_KEY env var)
            model: Model to use (default: gpt-5)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.system_prompt = SYSTEM_PROMPT
    
    def process_conversation(
        self, 
        user_message: str, 
        conversation_history: List[Dict[str, str]]
    ) -> Iterator[Dict[str, Any]]:
        """
        Process a conversation with tool calling support and streaming.
        
        Args:
            user_message: The user's message
            conversation_history: Previous conversation messages
            
        Yields:
            Dictionary with type ('content', 'tool_call', 'tool_result', 'done', 'error') and data
        """
        # Build messages list
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        max_iterations = 10  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call OpenAI API with streaming
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=TOOL_DEFINITIONS,
                    tool_choice="auto",
                    stream=True
                )
            except Exception as e:
                yield {
                    "type": "error",
                    "data": f"API Error: {str(e)}"
                }
                return
            
            # Process streaming response
            content_chunks = []
            tool_calls = []
            finish_reason = None
            
            for chunk in response:
                if not chunk.choices:
                    continue
                
                delta = chunk.choices[0].delta
                
                # Handle content
                if delta.content:
                    content_chunks.append(delta.content)
                    yield {
                        "type": "content",
                        "data": delta.content
                    }
                
                # Handle tool calls
                if delta.tool_calls:
                    for tool_call_delta in delta.tool_calls:
                        idx = tool_call_delta.index
                        if idx is not None:
                            # Ensure we have enough tool calls in our list
                            while len(tool_calls) <= idx:
                                tool_calls.append(None)
                            
                            if tool_calls[idx] is None:
                                tool_calls[idx] = {
                                    "id": tool_call_delta.id or "",
                                    "type": "function",
                                    "function": {
                                        "name": tool_call_delta.function.name or "",
                                        "arguments": tool_call_delta.function.arguments or ""
                                    }
                                }
                            else:
                                # Update existing tool call
                                if tool_call_delta.id:
                                    tool_calls[idx]["id"] = tool_call_delta.id
                                if tool_call_delta.function.name:
                                    tool_calls[idx]["function"]["name"] = tool_call_delta.function.name
                                if tool_call_delta.function.arguments:
                                    tool_calls[idx]["function"]["arguments"] += tool_call_delta.function.arguments
                
                # Track finish reason
                if chunk.choices[0].finish_reason:
                    finish_reason = chunk.choices[0].finish_reason
            
            # Add assistant message with content
            if content_chunks:
                messages.append({
                    "role": "assistant",
                    "content": "".join(content_chunks)
                })
            
            # Handle tool calls
            if tool_calls and finish_reason == "tool_calls":
                # Add assistant message with tool calls
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": tc["id"],
                            "type": tc["type"],
                            "function": {
                                "name": tc["function"]["name"],
                                "arguments": tc["function"]["arguments"]
                            }
                        }
                        for tc in tool_calls if tc is not None
                    ]
                })
                
                # Execute each tool call
                for tool_call in tool_calls:
                    if tool_call is None:
                        continue
                    
                    # Yield tool call info
                    try:
                        arguments = json.loads(tool_call["function"]["arguments"])
                    except json.JSONDecodeError:
                        arguments = {}
                    
                    yield {
                        "type": "tool_call",
                        "data": {
                            "function_name": tool_call["function"]["name"],
                            "arguments": arguments
                        }
                    }
                    
                    # Execute tool
                    tool_result = execute_tool(
                        tool_call["function"]["name"],
                        arguments
                    )
                    
                    # Yield tool result
                    yield {
                        "type": "tool_result",
                        "data": {
                            "function_name": tool_call["function"]["name"],
                            "arguments": arguments,
                            "result": tool_result
                        }
                    }
                    
                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "content": json.dumps(tool_result),
                        "tool_call_id": tool_call["id"]
                    })
                
                # Continue loop to get assistant response
                continue
            
            # If finish_reason is "stop", we're done
            if finish_reason == "stop":
                yield {"type": "done", "data": None}
                break
        
        if iteration >= max_iterations:
            yield {
                "type": "error",
                "data": "Maximum iterations reached. Conversation may be incomplete."
            }
    
    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        max_iterations: int = 10
    ) -> Iterator[str]:
        """
        Stream a chat completion with tool calling support (legacy method for compatibility).
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            max_iterations: Maximum number of tool call iterations
            
        Yields:
            Text chunks from the streaming response
        """
        # Extract user message and history
        user_message = ""
        conversation_history = []
        
        for msg in messages:
            if msg["role"] == "user":
                if user_message:
                    conversation_history.append({"role": "user", "content": user_message})
                user_message = msg["content"]
            elif msg["role"] == "assistant":
                conversation_history.append(msg)
        
        # Use the new process_conversation method
        for event in self.process_conversation(user_message, conversation_history):
            if event["type"] == "content":
                yield event["data"]
    
    def chat(
        self,
        messages: List[Dict[str, str]]
    ) -> str:
        """
        Non-streaming chat completion with tool calling support.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            
        Returns:
            Complete response text
        """
        return "".join(self.chat_stream(messages))
