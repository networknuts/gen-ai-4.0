from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
import asyncio
from openai import OpenAI
from dotenv import load_dotenv
import json 

# ENVIRONMENT SETUP

load_dotenv()
client = OpenAI()

# SYSTEM PROMPT FOR MCP CLIENT

SYSTEM_PROMPT = f"""
You are an MCP Client AI Assistant with access to external tools.

Once you receive the user's request, check available tools and make a decision
on whether the user's query should be answered via the tool or via internal data.

Based upon your decision, continue answering the query of the user.
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
            
            # ASK QUESTION AND DECIDE WHICH TOOL TO EXECUTE
            response = client.responses.create(
                model="gpt-5.4-mini",
                instructions=SYSTEM_PROMPT,
                input=query,
                tools=openai_tools
            )
            # DETECT TOOL CALL
            tool_call = None
            for item in response.output:
                if item.type == "function_call":
                    tool_call = item
                    break 
            # EXECUTE THE FUNCTION
            if tool_call:
                tool_name = tool_call.name
                args = json.loads(tool_call.arguments)
                print(f"\nLLM SELECTED TOOL: {tool_name}\n")

                result = await session.call_tool(tool_name,args)
                print("\nTOOL RESULT\n")
                for item in result.content:
                    if hasattr(item, "text"):
                        print(item.text)
                    else:
                        print(item)
            else:
                print("NO TOOL EXECUTED, GETTING OUTPUT FROM LLM DATA")
                print(response.output_text)
                    


asyncio.run(main())