"""
YellowPages entrypoint: runs the MCP server.
Use: uv run main.py  (or: uv run python -m src.mcp.server)
"""
import sys

from src.mcp.server import mcp

if __name__ == "__main__":
    print("YellowPages MCP server started (stdio). Waiting for requests.", file=sys.stderr)
    mcp.run()
