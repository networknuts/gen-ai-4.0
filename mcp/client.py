from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
import asyncio
from openai import OpenAI
from dotenv import load_dotenv

# ENVIRONMENT SETUP

load_dotenv()
client = OpenAI()

# SYSTEM PROMPT FOR MCP CLIENT

SYSTEM_PROMPT = f"""
You are an MCP Client AI Assistant with access to external tools.

Given the user's request, you must call the appropriate tool.

Do not answer from memory when a tool is available to perform the required job.

"""

# CONVERT MCP TOOL INTO TOOL SCHEMA OF OPENAI

def convert_tool(tool):
    return {
        "type": "function",
        "name": tool.name,
        "description": tool.description or "",
        "parameters": tool.inputSchema
    }

# MAIN CLIENT LOGIC

async def main():
    query = input("HUMAN QUERY: ")

    async with streamable_http_client("http://localhost:8000/mcp") as (
        read_stream,
        write_stream,
        input_stream
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tool_list = await session.list_tools()
            tools = tool_list.tools

            openai_tools = [convert_tool(t) for t in tools]
            print(openai_tools)


asyncio.run(main())