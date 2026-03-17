import { NavLink } from 'react-router-dom'

const REPO_URL = import.meta.env.VITE_REPO_URL || 'https://github.com/ethank64/yellow-pages'

export default function BaseLayout({ children }) {
  return (
    <div className="base-layout">
      <header className="site-header">
        <div className="site-header-inner">
          <NavLink to="/" className="site-logo">YellowPages</NavLink>
          <p className="site-tagline">Discover and execute API operations</p>
          <nav className="site-nav" aria-label="Main">
            <NavLink to="/" end className={({ isActive }) => 'site-nav-link' + (isActive ? ' site-nav-link--active' : '')}>Home</NavLink>
            <NavLink to="/docs" className={({ isActive }) => 'site-nav-link' + (isActive ? ' site-nav-link--active' : '')}>Docs</NavLink>
          </nav>
        </div>
      </header>
      <main className="site-main">
        {children}
      </main>
      <footer className="site-footer">
        <div className="site-footer-inner">
          <p className="site-footer-tagline">Your agent stays in control.</p>
          <div className="site-footer-links">
            <a href={REPO_URL} target="_blank" rel="noopener noreferrer" className="site-footer-link">Source</a>
          </div>
        </div>
      </footer>
    </div>
  )
}
