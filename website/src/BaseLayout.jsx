import { NavLink, useLocation } from 'react-router-dom'

const REPO_URL = import.meta.env.VITE_REPO_URL || 'https://github.com/ethank64/yellow-pages'

export default function BaseLayout({ children }) {
  const location = useLocation()
  return (
    <div className="base-layout">
      <header className="site-header">
        <div className="site-header-inner">
          <div className="site-header-brand">
            <NavLink to="/" className="site-logo">YellowPages</NavLink>
            <p className="site-tagline">Discover and execute API operations</p>
          </div>
          <nav className="site-nav" aria-label="Main">
            <NavLink to="/" end className={({ isActive }) => 'site-nav-link' + (isActive ? ' site-nav-link--active' : '')}>Home</NavLink>
            <NavLink to="/docs" className={({ isActive }) => 'site-nav-link' + (isActive ? ' site-nav-link--active' : '')}>Docs</NavLink>
          </nav>
        </div>
      </header>
      <main className="site-main" key={location.pathname}>
        {children}
      </main>
      <footer className="site-footer">
        <div className="site-footer-inner">
          <p className="site-footer-tagline">Your agent stays in control.</p>
          <div className="site-footer-links">
            <NavLink to="/docs" className="site-footer-link">Docs</NavLink>
            <a href={REPO_URL} target="_blank" rel="noopener noreferrer" className="site-footer-link">Source</a>
          </div>
        </div>
      </footer>
    </div>
  )
}
