export default function SchemaFormat() {
  return (
    <>
      <h1 className="docs-title">Schema format</h1>
      <p>
        The server expects a standard OpenAPI 3.x file with a{' '}
        <code>servers</code> block. It converts each operation into a
        simplified shape: <code>name</code>, <code>tags</code>, <code>url</code>
        , <code>method</code>, <code>parameters</code>, <code>responses</code>.
        The bundled <code>sample_schema.json</code> (Nager.Date holiday API) is
        there so you can try it immediately.
      </p>
    </>
  )
}
