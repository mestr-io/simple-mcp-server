# mcp_ollama_client.py
import ollama
import requests
import json
import uuid # Import the uuid library for generating unique IDs

# --- Configuration ---
OLLAMA_MODEL = "llama3.2" # Updated model as per your query
MCP_SERVER_URL = "http://localhost:8001" # Address of our MCP Time Server

# --- MCP Client Functions to Interact with MCP Server ---

def get_mcp_tool_definitions():
    """
    Fetches the schema (definitions) of tools available from the MCP server.
    This is what the LLM will 'read' to understand what capabilities it has.
    """
    try:
        # Make a GET request to the MCP server's /mcp/v1/tools endpoint
        response = requests.get(f"{MCP_SERVER_URL}/mcp/v1/tools")
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        return response.json().get("tools", []) # Extract the 'tools' list from the response
    except requests.exceptions.RequestException as e:
        print(f"Error fetching tool definitions from MCP server: {e}")
        return [] # Return an empty list if there's an error

def call_mcp_server_tool(tool_name: str, arguments: dict):
    """
    Sends a request to the MCP server to execute a specific tool.
    """
    payload = {
        "tool_name": tool_name,
        "arguments": arguments
    }
    try:
        # Make a POST request to the MCP server's /mcp/v1/call endpoint
        response = requests.post(f"{MCP_SERVER_URL}/mcp/v1/call", json=payload)
        response.raise_for_status()
        return response.json() # Return the JSON response from the tool execution
    except requests.exceptions.RequestException as e:
        print(f"Error calling tool '{tool_name}' on MCP server: {e}")
        return {"tool_name": tool_name, "error": str(e)} # Return an error if the call fails

# --- Main Chat Orchestration Logic ---

def chat_with_ollama_and_tools(user_prompt: str):
    """
    Manages the conversation flow, including LLM interaction and MCP tool use.
    """
    messages = [] # Stores the conversation history for the LLM

    # 1. MCP Client: Discover available tools from the MCP Server
    mcp_tool_definitions = get_mcp_tool_definitions()
    
    if not mcp_tool_definitions:
        print("No MCP tools available from the server. Proceeding with basic LLM chat.")
        # If no tools are found, just perform a regular chat with the LLM
        messages.append({"role": "user", "content": user_prompt})
        response = ollama.chat(model=OLLAMA_MODEL, messages=messages)
        print(f"\nAI (without tools): {response['message']['content']}")
        return

    # 2. MCP Client: Inform the LLM about the available tools
    # This is done via a 'system' message or a dedicated 'tools' parameter in the LLM API call.
    # Ollama's Python library supports a 'tools' parameter directly.
    
    # We still provide a system message to guide the LLM's behavior regarding tool use.
    # Enhanced system message to guide the LLM more specifically
    system_message_content = f"""You are a helpful assistant.
You have access to tools to help answer user questions.
Specifically, you can use the 'get_current_time' tool to find out the current time in UTC.
When a user asks a question about the current time or date,
you MUST respond by calling the 'get_current_time' tool.
Otherwise, answer normally.
Here are the tool definitions: {json.dumps(mcp_tool_definitions)}
"""
    messages.append({"role": "system", "content": system_message_content})
    messages.append({"role": "user", "content": user_prompt})

    print(f"\n--- User Prompt: '{user_prompt}' ---")
    print(f"--- Sending prompt and tool definitions to local Ollama ({OLLAMA_MODEL}) ---")

    # Loop to handle multi-turn interactions if tools are called
    while True:
        # 3. MCP Client: Call the LLM (Ollama)
        # Pass the conversation history and the tool definitions to Ollama
        response = ollama.chat(model=OLLAMA_MODEL, messages=messages, tools=mcp_tool_definitions)

        # 4. MCP Client: Check LLM's response for tool calls
        tool_calls = response.get('message', {}).get('tool_calls')

        if tool_calls:
            # The LLM wants to use a tool!
            print("\n--- LLM wants to call tools! ---")
            
            # Iterate through all tool calls suggested by the LLM (can be multiple)
            for tool_call in tool_calls:
                tool_name = tool_call['function']['name']
                tool_arguments = tool_call['function']['arguments']
                # Safely get tool_call_id, generate a UUID if not present
                # This handles cases where the LLM might not provide an 'id' directly
                tool_call_id = tool_call.get('id', str(uuid.uuid4())) # Generate a unique ID if LLM doesn't provide one

                print(f"--- LLM requested tool: '{tool_name}' with arguments: {tool_arguments} ---")

                # 5. MCP Client: Execute the tool call via the MCP Server
                tool_output_from_mcp_server = call_mcp_server_tool(tool_name, tool_arguments)

                # 6. MCP Client: Add the tool's output back to the conversation history
                # This is crucial for the LLM to see the result of its tool request
                if "error" in tool_output_from_mcp_server:
                    print(f"--- Tool execution failed: {tool_output_from_mcp_server['error']} ---")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": json.dumps({"error": tool_output_from_mcp_server['error']})
                    })
                else:
                    print(f"--- Tool execution successful. Output: {tool_output_from_mcp_server['output']} ---")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": json.dumps(tool_output_from_mcp_server['output'])
                    })
            
            # After executing all tool calls and adding their outputs,
            # loop back to call Ollama again. The LLM will then use the tool outputs
            # to generate a final, informed response.
            print("\n--- Sending tool output back to LLM for final response generation ---")
            continue # Continue the while loop

        else:
            # The LLM generated a final text response (no more tool calls needed)
            final_response_content = response['message']['content']
            print(f"\n--- AI Final Response: {final_response_content} ---")
            break # Exit the loop

# --- Main execution block ---
if __name__ == "__main__":
    print("--- Starting MCP Ollama Client ---")
    print(f"Make sure Ollama is running and model '{OLLAMA_MODEL}' is pulled.")
    print(f"Also ensure the MCP Time Server is running on {MCP_SERVER_URL}.")

    # Test cases:
    # This prompt should trigger the 'get_current_time' tool
    prompt_to_test_tool = "What time is it right now?"
    chat_with_ollama_and_tools(prompt_to_test_tool)

    # This prompt should NOT trigger a tool, as it doesn't require external data
    # prompt_no_tool = "Tell me a short story about a brave knight."
    # chat_with_ollama_and_tools(prompt_no_tool)
