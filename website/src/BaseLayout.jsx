export default function BaseLayout({ children }) {
  return (
    <div className="base-layout">
      <header className="site-header">
        <div className="site-header-inner">
          <a href="/" className="site-logo">YellowPages</a>
          <p className="site-tagline">Discover and execute API operations</p>
        </div>
      </header>
      <main className="site-main">
        {children}
      </main>
      <footer className="site-footer">
        <div className="site-footer-inner">
          <span>Your agent stays in control.</span>
        </div>
      </footer>
    </div>
  )
}
