import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():

    # Start our MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "app.mcp.server"]
    )

    # Connect to MCP server
    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            # Initialize MCP connection
            await session.initialize()

            # Show available tools
            tools = await session.list_tools()

            print("\n===== MCP TOOLS =====")

            for tool in tools.tools:
                print("-", tool.name)

            # Test previous meetings
            result = await session.call_tool(
                "search_previous_meetings",
                arguments={
                    "user_id": 1,
                    "limit": 5
                }
            )

            print("\n===== PREVIOUS MEETINGS =====")
            print(result.content)

            # Test previous tasks
            result = await session.call_tool(
                "get_previous_tasks",
                arguments={
                    "user_id": 1,
                    "limit": 10
                }
            )

            print("\n===== PREVIOUS TASKS =====")
            print(result.content)


if __name__ == "__main__":
    asyncio.run(main())