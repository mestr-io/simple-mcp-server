# mcp_time_server.py
from fastapi import FastAPI
from datetime import datetime, timezone

import uvicorn
import json

app = FastAPI(
    title="Time MCP Server",
    description="A simple MCP server to provide the current time."
)

@app.post("/mcp/v1/call")
async def call_tool(tool_call: dict):
    """
    Handles incoming tool call requests from the MCP Client.
    It expects a JSON payload with 'tool_name' and 'arguments'.
    """
    tool_name = tool_call.get("tool_name")
    tool_args = tool_call.get("arguments", {})

    print(f"\n--- MCP Server Received Tool Call: {tool_name} with args {tool_args} ---")

    if tool_name == "get_current_time":
        # Simulate fetching the current time (e.g., from a real API or system clock)
        current_utc_time = datetime.now(timezone.utc).isoformat() + "Z"
        print(f"--- MCP Server Executing: Getting current UTC time: {current_utc_time} ---")
        # Return the output in a structured format as expected by the MCP protocol
        return {"tool_name": tool_name, "output": {"current_time_utc": current_utc_time}}
    else:
        # Handle cases where the requested tool is not supported by this server
        return {"tool_name": tool_name, "error": f"Tool '{tool_name}' not found or supported by this server."}

@app.get("/mcp/v1/tools")
async def get_tools_definition():
    """
    Provides the MCP tool definitions (schema) that this server offers.
    The MCP Client will fetch this and pass it to the LLM.
    """
    print("\n--- MCP Server Providing Tool Definitions ---")
    return {
        "tools": [
            {
                "name": "get_current_time",
                "description": "Get the current time in UTC. Useful for answering questions about the current time or date.",
                "parameters": {
                    "type": "object",
                    "properties": {}, # This tool doesn't require any input parameters
                    "required": []
                }
            }
        ]
    }

if __name__ == "__main__":
    # To run this server: uvicorn mcp_time_server:app --port 8001 --reload
    print("Starting MCP Time Server on http://localhost:8001")
    # Run the FastAPI application using uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)

