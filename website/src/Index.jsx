export default function Index() {
  return (
    <section className="index-hero">
      <div className="index-hero-inner">
        <h1 className="index-title">
          API operations, at your command
        </h1>
        <p className="index-lead">
          Load an OpenAPI schema once. Discover operations with natural language.
          Execute with the parameters you choose. No LLM inside the server—your
          caller agent decides what to call and when.
        </p>
        <div className="index-cta">
          <a
            href="https://github.com"
            className="index-cta-link"
            target="_blank"
            rel="noopener noreferrer"
          >
            Get started
          </a>
        </div>
      </div>
    </section>
  )
}
