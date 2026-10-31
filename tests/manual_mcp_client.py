
import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "sql_risk_agent.mcp_server"],
        env={
            **os.environ,
            "PYTHONPATH": "src",
        },
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            # Discover tools exposed by the server
            tools = await session.list_tools()

            print("Available MCP tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}")

            # Call our SQL risk analysis tool
            result = await session.call_tool(
                "analyze_sql_risk",
                arguments={
                    "sql": "DELETE FROM orders;",
                    "use_llm": False,
                },
            )

            print("\nMCP tool response:")

            if result.isError:
                print("MCP tool reported an error")

            if result.structuredContent is not None:
                print(json.dumps(
                    result.structuredContent,
                    indent=2,
                ))
            else:
                for content in result.content:
                    if content.type == "text":
                        print(content.text)


if __name__ == "__main__":
    asyncio.run(main())

