"""
Streamlit application for the Pharmacist Assistant.
Provides a web interface for interacting with the pharmacy agent.
"""

import streamlit as st
import os
from dotenv import load_dotenv
from app.agent.agent import PharmacistAgent

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Pharmacist Assistant",
    page_icon="💊",
    layout="wide"
)

def format_tool_call_title(function_name: str, arguments: dict) -> str:
    """Format tool call title with function name and parameters."""
    # Format parameters as key=value pairs
    param_parts = []
    for key, value in arguments.items():
        # Truncate long values for display
        value_str = str(value)
        if len(value_str) > 30:
            value_str = value_str[:27] + "..."
        param_parts.append(f"{key}={value_str}")
    
    params_str = ", ".join(param_parts) if param_parts else "no parameters"
    return f"Tool Call: {function_name} - {params_str}"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    # Initialize agent (will use OPENAI_API_KEY from environment)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("Please set OPENAI_API_KEY environment variable in .env file")
        st.stop()
    
    try:
        st.session_state.agent = PharmacistAgent(api_key=api_key, model="gpt-5")
    except Exception as e:
        st.error(f"Initialization Error: {str(e)}")
        st.stop()


# Title and header
st.title("💊 Pharmacist Assistant")
st.markdown("Your AI-powered pharmacy assistant for prescription management and medication information.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display tool calls if present
        if "tool_calls" in message:
            for tool_call in message["tool_calls"]:
                title = format_tool_call_title(
                    tool_call['function_name'],
                    tool_call.get("arguments", {})
                )
                with st.expander(title, expanded=False):
                    st.write(f"**Function:** `{tool_call['function_name']}`")
                    st.write("**Arguments:**")
                    st.json(tool_call["arguments"])
                    st.write("**Result:**")
                    st.json(tool_call["result"])

# Chat input
if prompt := st.chat_input("How can I help you today?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        thinking_placeholder = st.empty()
        full_response = ""
        tool_calls_for_message = []
        first_chunk_received = False
        
        # Show thinking indicator immediately
        thinking_placeholder.markdown("💭 *Processing your request...*")
        
        # Process conversation with streaming
        try:
            for event in st.session_state.agent.process_conversation(
                prompt,
                [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in st.session_state.messages[:-1]  # Exclude current message
                ]
            ):
                event_type = event.get("type")
                event_data = event.get("data")
                
                if event_type == "content":
                    # Hide thinking indicator on first content chunk
                    if not first_chunk_received:
                        thinking_placeholder.empty()
                        first_chunk_received = True
                    
                    # Stream content
                    full_response += event_data
                    message_placeholder.markdown(full_response + "▌")
                
                elif event_type == "tool_call":
                    # Hide thinking indicator on first tool call
                    if not first_chunk_received:
                        thinking_placeholder.empty()
                        first_chunk_received = True
                    
                    # Store tool call info
                    tool_calls_for_message.append({
                        "function_name": event_data["function_name"],
                        "arguments": event_data["arguments"],
                        "result": None
                    })
                
                elif event_type == "tool_result":
                    # Update tool call with result
                    if tool_calls_for_message:
                        tool_calls_for_message[-1]["result"] = event_data.get("result", event_data)
                        
                        # Display tool result
                        last_tool = tool_calls_for_message[-1]
                        title = format_tool_call_title(
                            last_tool['function_name'],
                            last_tool.get("arguments", {})
                        )
                        with st.expander(title, expanded=False):
                            st.write(f"**Function:** `{last_tool['function_name']}`")
                            st.write("**Arguments:**")
                            st.json(last_tool["arguments"])
                            st.write("**Result:**")
                            st.json(last_tool["result"])
                
                elif event_type == "error":
                    thinking_placeholder.empty()
                    st.error(f"Error: {event_data}")
                    break
                
                elif event_type == "done":
                    # Hide thinking indicator if still showing
                    thinking_placeholder.empty()
                    # Finalize response
                    message_placeholder.markdown(full_response)
                    break
            
            # Update final message display
            if full_response:
                message_placeholder.markdown(full_response)
            
            # Add assistant message to history
            assistant_message = {
                "role": "assistant",
                "content": full_response
            }
            if tool_calls_for_message:
                assistant_message["tool_calls"] = tool_calls_for_message
            
            st.session_state.messages.append(assistant_message)
        
        except Exception as e:
            # Hide thinking indicator on error
            thinking_placeholder.empty()
            error_msg = f"An error occurred: {str(e)}"
            st.error(error_msg)
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg
            })

# Sidebar with information
with st.sidebar:
    st.header("About")
    st.markdown("""
    This assistant can help you with:
    
    - **Medication Stock Check** - Check if medications are in stock
    - **Medication Information** - Get details about medications and usage
    - **Prescription Verification** - Verify your prescription status
    
    **Note:** This assistant provides factual information only.
    For medical advice, please consult your healthcare provider.
    """)
    
    st.header("Quick Actions")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
