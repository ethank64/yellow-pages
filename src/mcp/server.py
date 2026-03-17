"""
YellowPages MCP server: two tools for the caller agent.
- discover: RAG only, returns matching operations (ID + schema). No LLM inside.
- execute: run an operation by ID with given params. Caller chooses what to call.
"""
import os
import sys

from dotenv import load_dotenv

load_dotenv()

from mcp.server.fastmcp import FastMCP

from .rag import discover, execute

mcp = FastMCP("YellowPages")


@mcp.tool()
def discover_operations(query: str, k: int = 5) -> list[dict]:
    """
    Discover which API operations match a natural-language query. Uses RAG over the
    loaded OpenAPI schema; returns a list of operation entries (operation name, method,
    url, parameters with name/type/required). Use this to find tool IDs, then call
    execute_operation with the chosen operation_name and params. No execution happens here.
    """
    return discover(query=query, k=k)


@mcp.tool()
def execute_operation(
    operation_name: str,
    path_params: dict | None = None,
    query_params: dict | None = None,
    body_data: dict | None = None,
) -> str:
    """
    Execute one API operation by name. Use operation_name from discover_operations;
    provide path_params, query_params, and optionally body_data as required by the schema.
    Returns the API response body or an error string.
    """
    return execute(
        operation_name=operation_name,
        path_params=path_params,
        query_params=query_params,
        body_data=body_data,
    )


if __name__ == "__main__":
    transport = os.environ.get("YELLOW_PAGES_TRANSPORT", "stdio")
    if transport == "streamable-http":
        print(
            "YellowPages MCP server started (streamable-http). Waiting for requests.",
            file=sys.stderr,
        )
        mcp.run(transport="streamable-http")
    else:
        print("YellowPages MCP server started (stdio). Waiting for requests.", file=sys.stderr)
        mcp.run()
