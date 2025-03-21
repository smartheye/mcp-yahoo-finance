import anyio
import httpx
import click
from mcp.server.lowlevel import Server
import mcp.types as types

from .tool import get_current_price

async def fetch_website(
    url: str,
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    headers = {
        "User-Agent": "MCP Test Server (github.com/modelcontextprotocol/python-sdk)"
    }
    async with httpx.AsyncClient(follow_redirects=True, headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
        return [types.TextContent(type="text", text=response.text)]

@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(port: int, transport: str) -> int:

    app = Server("mcp-yfinance-service")

    @app.call_tool()
    async def tool(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name != "get_current_price":
            raise ValueError(f"Unknown tool: {name}")
        if "symbol" not in arguments:
            raise ValueError("Missing required argument 'symbol'")
        value = await get_current_price(arguments["symbol"])
        return [types.TextContent(type="text", text=value)]

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="get_current_price",
                description="获取股票的当前价格",
                inputSchema={
                    "type": "object",
                    "required": ["symbol"],
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "股票代码",
                        }
                    },
                },
            )
        ]

    if transport == "sse":
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Mount, Route

        sse = SseServerTransport("/messages/")

        # Define handler functions
        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        # Mount the SSE server to the existing ASGI server
        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

        import uvicorn

        uvicorn.run(starlette_app, host="0.0.0.0", port=port)
    else:
        from mcp.server.stdio import stdio_server

        async def arun():
            async with stdio_server() as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        anyio.run(arun)
    return 0