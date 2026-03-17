# YellowPages

**Discover and execute API operations. Your agent stays in control.**

YellowPages is an MCP (Model Context Protocol) server that exposes two tools: discover (RAG over an OpenAPI schema, returns matching operations with their schema) and execute (runs an operation by ID with given params). No LLM inside the server—your caller agent chooses which operation and parameters to use.

---

## Why it exists

APIs are everywhere, but using them usually means reading specs, copying URLs, and wiring parameters. YellowPages inverts that: you load an OpenAPI schema once and index it, then your MCP host (e.g. Cursor) can call discover with a natural-language query to get matching operations (with IDs and JSON schema), then call execute with the chosen operation and params. The server does RAG for discovery and runs the HTTP call; the caller agent decides what to call and with what arguments.

---

## How it works

There are two applications:

1. **Indexer** – Build the vector DB once (or when the schema changes). Run `uv run python -m src.indexer` with your OpenAPI schema path and Chroma directory (env or `--schema-path` / `--chroma-dir`). This flattens the schema into operations and indexes them in Chroma with local embeddings (sentence-transformers/all-MiniLM-L6-v2 by default).
2. **MCP server** – Run `uv run main.py` to start the server. It loads the *existing* Chroma index and schema (the indexer must have been run first). The server exposes two tools: **discover_operations** (RAG only; returns matching operations with ID and schema) and **execute_operation** (runs an operation by name with path/query/body params). No LLM inside the server; the caller agent chooses what to execute.

So: **build the index once; then the caller uses discover then execute.** The server expects the Chroma directory to already exist.

---

## Quick start

[UV](https://docs.astral.sh/uv/) is the best package manager ever, so naturally we use it here. From the project root:

```bash
uv sync
# Build the vector index from your OpenAPI schema (once, or when schema changes)
uv run python -m src.indexer
# Start the MCP server (no API key needed; uses local embeddings)
uv run main.py
```

Or run the server as `uv run python -m src.mcp.server` (same effect). The server uses **stdio** by default so hosts like Cursor can launch it as a subprocess. For remote use, set `YELLOW_PAGES_TRANSPORT=streamable-http` and run `uv run main.py`.

Without UV: `pip install -e .`, then run the indexer once (`python -m src.indexer`), then `python main.py` (or `python -m src.mcp.server`).

---

## Environment variables

| Variable | Description |
|----------|-------------|
| `YELLOW_PAGES_SCHEMA_PATH` | OpenAPI schema file (JSON or YAML). Default: `./sample_schema.json` |
| `YELLOW_PAGES_CHROMA_DIR` | Chroma vector DB directory. Default: `./chroma_db_agent_tools_v9`. If you switch embedding models, remove this directory (or use a new path) so the next indexer run re-indexes. |
| `YELLOW_PAGES_EMBEDDING_MODEL` | HuggingFace/sentence-transformers model name. Default: `sentence-transformers/all-MiniLM-L6-v2` |
| `YELLOW_PAGES_TRANSPORT` | `stdio` (default) or `streamable-http`. Only when running the server directly. |

---

## Adding to Cursor

In your MCP settings, add a server entry for YellowPages (UV recommended):

```json
{
  "mcpServers": {
    "yellow-pages": {
      "command": "uv",
      "args": ["run", "/path/to/yellow-pages/main.py"]
    }
  }
}
```

Without UV: `"command": "python", "args": ["/path/to/yellow-pages/main.py"]`.

Use **discover_operations** with a natural-language query to get matching API operations (with `name`, `method`, `url`, `parameters`), then use **execute_operation** with the chosen operation name and params. No API key required for the MCP server.

---

## Schema format

The server expects a standard OpenAPI 3.x file with a `servers` block. It converts each operation into a simplified shape: `name`, `tags`, `url`, `method`, `parameters`, `responses`. The bundled `sample_schema.json` (Nager.Date holiday API) is there so you can try it immediately.
