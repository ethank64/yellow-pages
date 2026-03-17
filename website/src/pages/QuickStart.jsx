export default function QuickStart() {
  return (
    <>
      <h1 className="docs-title">Quick start</h1>
      <p className="docs-lead">
        <a href="https://docs.astral.sh/uv/">UV</a> is the recommended package
        manager. From the project root:
      </p>
      <pre className="docs-code">
        <code>{`uv sync
# Build the vector index from your OpenAPI schema (once, or when schema changes)
uv run python -m src.indexer
# Start the MCP server (no API key needed; uses local embeddings)
uv run main.py`}</code>
      </pre>
      <p>
        Or run the server as <code>uv run python -m src.mcp.server</code> (same
        effect). The server uses <strong>stdio</strong> by default so hosts like
        Cursor can launch it as a subprocess. For remote use, set{' '}
        <code>YELLOW_PAGES_TRANSPORT=streamable-http</code> and run{' '}
        <code>uv run main.py</code>.
      </p>
      <p>
        Without UV: <code>pip install -e .</code>, then run the indexer once (
        <code>python -m src.indexer</code>), then <code>python main.py</code> (
        or <code>python -m src.mcp.server</code>).
      </p>
    </>
  )
}
