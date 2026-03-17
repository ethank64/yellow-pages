export default function AddingToCursor() {
  return (
    <>
      <h1 className="docs-title">Adding to Cursor</h1>
      <p>
        In your MCP settings, add a server entry for YellowPages (UV
        recommended):
      </p>
      <pre className="docs-code">
        <code>{`{
  "mcpServers": {
    "yellow-pages": {
      "command": "uv",
      "args": ["run", "/path/to/yellow-pages/main.py"]
    }
  }
}`}</code>
      </pre>
      <p>
        Without UV: <code>&quot;command&quot;: &quot;python&quot;, &quot;args&quot;: [&quot;/path/to/yellow-pages/main.py&quot;]</code>
      </p>
      <p>
        Use <strong>discover_operations</strong> with a natural-language query
        to get matching API operations (with <code>name</code>,{' '}
        <code>method</code>, <code>url</code>, <code>parameters</code>), then
        use <strong>execute_operation</strong> with the chosen operation name
        and params. No API key required for the MCP server.
      </p>
    </>
  )
}
