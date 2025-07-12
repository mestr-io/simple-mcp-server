MCP Ollama Time Tool Example
This project demonstrates a simple implementation of the Model Context Protocol (MCP) using a local Ollama Large Language Model (LLM) and a custom MCP server. It showcases how an AI client can orchestrate interactions between the LLM and external tools.

Actors
This setup involves three main components:

Ollama LLM: Your local Large Language Model (e.g., llama3.2) that processes natural language and decides when to use external tools.

MCP Server: A FastAPI application that exposes a simple "get current time" tool. In a real-world scenario, this would connect to various external services (databases, APIs, etc.).

MCP Client: A Python script that acts as the orchestrator. It communicates with the Ollama LLM, informs it about available tools from the MCP Server, executes tool calls when requested by the LLM, and feeds the results back to the LLM for a final response.

Prerequisites
Before you begin, ensure you have the following installed:

Python 3.8+: Download Python

Ollama: A local LLM server.

Download and install Ollama from ollama.com.

Pull a compatible model (e.g., llama3.2) from your terminal:

ollama pull llama3.2

Required Python Libraries:

pip install ollama requests fastapi uvicorn

Project Structure
You should have two Python files:

mcp_time_server.py (The MCP Server code)

mcp_ollama_client.py (The MCP Client code)

Getting Started
To run the full example, you need to start each component in a separate terminal.

1. Start Ollama (Your LLM)
Ollama runs as a background service by default after installation. You can verify it's running by visiting http://localhost:11434 in your web browser.

If it's not running or you want to explicitly start it in the foreground for debugging, open a terminal and run:

ollama run llama3.2
# Or simply: ollama serve

Leave this terminal running.

2. Start the MCP Server
The MCP server (mcp_time_server.py) provides the get_current_time tool.

Open a new terminal window, navigate to the directory where you saved mcp_time_server.py, and run:

uvicorn mcp_time_server:app --port 8001 --reload

You should see output indicating the server is running on http://127.0.0.1:8001. Leave this terminal running.

3. Start the MCP Client
The MCP client (mcp_ollama_client.py) will orchestrate the interaction.

Open a third terminal window, navigate to the directory where you saved mcp_ollama_client.py, and run:

python mcp_ollama_client.py

Expected Output
When you run the mcp_ollama_client.py, you should see output similar to this:

--- Starting MCP Ollama Client ---
Make sure Ollama is running and model 'llama3.2' is pulled.
Also ensure the MCP Time Server is running on http://localhost:8001.

--- User Prompt: 'What time is it right now?' ---
--- Sending prompt and tool definitions to local Ollama (llama3.2) ---

--- LLM wants to call tools! ---
--- LLM requested tool: 'get_current_time' with arguments: {} ---
--- Tool execution successful. Output: {'current_time_utc': 'YYYY-MM-DDTHH:MM:SS.mmmmmmZ'} ---

--- Sending tool output back to LLM for final response generation ---

--- AI Final Response: The current time is YYYY-MM-DDTHH:MM:SS.mmmmmmZ UTC. ---

(The YYYY-MM-DDTHH:MM:SS.mmmmmmZ will be replaced by the actual current UTC time.)

You will also see corresponding log messages in your MCP Server terminal, indicating that it received the tool definition request and then the tool call request.

How it Works
The mcp_ollama_client.py starts by asking the mcp_time_server.py for its available tool definitions.

The client then sends a prompt to the Ollama LLM, along with the definition of the get_current_time tool.

The LLM, recognizing that "What time is it right now?" can be answered by the get_current_time tool, instructs the client to call this tool.

The client receives this instruction and makes an HTTP request to the mcp_time_server.py to execute get_current_time.

The mcp_time_server.py gets the actual current time and sends it back to the client.

The client then sends this factual information (the current time) back to the Ollama LLM.

Finally, the LLM, now having the current time in its context, generates a natural language response to the user.