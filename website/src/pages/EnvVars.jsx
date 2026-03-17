export default function EnvVars() {
  return (
    <>
      <h1 className="docs-title">Environment variables</h1>
      <div className="docs-table-wrap">
        <table className="docs-table">
          <thead>
            <tr>
              <th>Variable</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><code>YELLOW_PAGES_SCHEMA_PATH</code></td>
              <td>
                OpenAPI schema file (JSON or YAML). Default:{' '}
                <code>./sample_schema.json</code>
              </td>
            </tr>
            <tr>
              <td><code>YELLOW_PAGES_CHROMA_DIR</code></td>
              <td>
                Chroma vector DB directory. Default:{' '}
                <code>./chroma_db_agent_tools_v9</code>. If you switch embedding
                models, remove this directory (or use a new path) so the next
                indexer run re-indexes.
              </td>
            </tr>
            <tr>
              <td><code>YELLOW_PAGES_EMBEDDING_MODEL</code></td>
              <td>
                HuggingFace/sentence-transformers model name. Default:{' '}
                <code>sentence-transformers/all-MiniLM-L6-v2</code>
              </td>
            </tr>
            <tr>
              <td><code>YELLOW_PAGES_TRANSPORT</code></td>
              <td>
                <code>stdio</code> (default) or <code>streamable-http</code>.
                Only when running the server directly.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </>
  )
}
