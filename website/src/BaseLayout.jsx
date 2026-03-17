import { Link } from 'react-router-dom'

export default function BaseLayout({ children }) {
  return (
    <div className="base-layout">
      <header className="site-header">
        <div className="site-header-inner">
          <Link to="/" className="site-logo">YellowPages</Link>
          <p className="site-tagline">Discover and execute API operations</p>
          <nav className="site-nav" aria-label="Main">
            <Link to="/" className="site-nav-link">Home</Link>
            <Link to="/docs/quick-start" className="site-nav-link">Docs</Link>
          </nav>
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
