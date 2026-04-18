from mcp.server.fastmcp import FastMCP
import wikipedia

# SETUP THE MCP SERVER

mcp = FastMCP("Research Server", json_response=True)


# SETUP THE WIKIPEDIA TOOL

@mcp.tool()
def wikipedia_search(topic: str):
    """
    Get wikipedia summary of any topic by providing the relevant topic.
    This wikipedia search tool is limited to only providing 10 lines on the
    respective topic.
    """
    try:
        return wikipedia.summary(topic,sentences=10)
    except Exception as e:
        return str(e)

@mcp.tool()
def database_search(query: str):
    """
    Search internal company database for any particular term and provide top 10 results matching the 
    query.
    """
    print("tool executed successfully!")

mcp.run(transport="streamable-http")