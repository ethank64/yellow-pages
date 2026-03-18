import { Outlet, NavLink } from 'react-router-dom'

const docLinks = [
  { to: '/docs/quick-start', label: 'Quick start' },
  { to: '/docs/env-vars', label: 'Environment variables' },
  { to: '/docs/adding-to-cursor', label: 'Adding to Cursor' },
  { to: '/docs/schema-format', label: 'Schema format' },
]

export default function DocsLayout() {
  return (
    <div className="docs-layout">
      <nav className="docs-nav" aria-label="Docs">
        <p className="docs-nav-title">Documentation</p>
        <ul className="docs-nav-list">
          {docLinks.map(({ to, label }) => (
            <li key={to}>
              <NavLink
                to={to}
                className={({ isActive }) =>
                  'docs-nav-link' + (isActive ? ' docs-nav-link--active' : '')
                }
                end={false}
              >
                {label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      <article className="docs-content">
        <Outlet />
      </article>
    </div>
  )
}
