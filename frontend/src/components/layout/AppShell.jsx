import { useState } from 'react'
import {
  Link, NavLink,Outlet, useNavigate,
} from 'react-router'

import { useAuth } from '../../contexts/useAuth'

const navigationItems = [
  {
 to: '/dashboard',
    label: 'Dashboard',
  },
  {
    to: '/library',
    label: 'Asset library',
  },
  {
    to: '/collections',
    label: 'Collections',
  },
  {
    to: '/upload',
    label: 'Upload',
    roles: ['editor', 'admin'],
  },
  {
    to: '/review',
    label: 'Review queue',
    roles: ['admin'],
  },
  {
    to: '/profile',
    label: 'Profile',
  },
]

const roleLabels = {
  viewer: 'Viewer',
  editor: 'Editor',
  admin: 'Administrator',
}

export function AppShell() {
  const {
    user,
    logout,
  } = useAuth()

  const navigate = useNavigate()

  const [loggingOut, setLoggingOut] =
    useState(false)

  const [logoutError, setLogoutError] =
    useState('')

  const displayName = (
    [
      user?.first_name,
      user?.last_name,
    ]
      .filter(Boolean)
      .join(' ') ||
    user?.email ||
    'Streamline user'
  )

  const visibleNavigation =
    navigationItems.filter((item) => {
      return (
        !item.roles ||
        item.roles.includes(user?.role)
      )
    })

  async function handleLogout() {
    setLoggingOut(true)
    setLogoutError('')

    try {
      await logout()

      navigate('/login', {
        replace: true,
      })
    } catch {
      setLogoutError(
        'Unable to log out. Please try again.',
      )
    } finally {
      setLoggingOut(false)
    }
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <Link
          to="/dashboard"
          className="app-brand"
        >
          Streamline
        </Link>

 <div className="account-summary">
          <div>
            <strong>{displayName}</strong>
            <span>
              {roleLabels[user?.role] ?? 'User'}
            </span>
          </div>

          <button
            type="button"
            disabled={loggingOut}
            onClick={handleLogout}
          >
            {loggingOut
              ? 'Logging out…'
              : 'Log out'}
          </button>
        </div></header>

<div className="app-body">
        <aside className="app-sidebar">
          <nav aria-label="Primary navigation">
            {visibleNavigation.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) => (
                  isActive
                    ? 'nav-link nav-link-active'
                    : 'nav-link'
                )}
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </aside>

        <main className="app-content">
          {logoutError && (
            <p role="alert">
              {logoutError}
            </p>
          )}
          <Outlet />
        </main>
      </div>
    </div>
  )
}