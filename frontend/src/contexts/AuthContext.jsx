
/**
 * Authentication context provider component.
 */

import {
  useEffect,
  useState,
} from 'react'

import {
  getCurrentUser,
  initialiseCsrf,
  loginUser,
  logoutUser,
  registerUser,
} from '../api/auth'
import { ApiError } from '../api/client'
import { AuthContext } from './auth-context'

/**
 * Checks if the given error indicates an unauthenticated state.
 */

function isUnauthenticated(error) {
  return (
    error instanceof ApiError &&
    (
      error.status === 401 ||
      error.status === 403
    )
  )
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    async function loadSession() {
      try {
        await initialiseCsrf()

        const currentUser =
          await getCurrentUser()

        if (!cancelled) {
          setUser(currentUser)
        }
      } catch (error) {
        if (
          !cancelled &&
          !isUnauthenticated(error)
        ) {
          console.error(
            'Unable to load the user session.',
            error,
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadSession()

    return () => {
      cancelled = true
    }
  }, [])

  async function refreshUser() {
    try {
      const currentUser =
        await getCurrentUser()

      setUser(currentUser)
      return currentUser
    } catch (error) {
      if (isUnauthenticated(error)) {
        setUser(null)
        return null
      }

      throw error
    }
  }

  async function login(credentials) {
    await initialiseCsrf()

    const authenticatedUser =
      await loginUser(credentials)

    setUser(authenticatedUser)
    return authenticatedUser
  }

  async function register(details) {
    await initialiseCsrf()

    const registeredUser =
      await registerUser(details)

    setUser(registeredUser)
    return registeredUser
  }

  async function logout() {
    await logoutUser()
    setUser(null)
  }

  const contextValue = {
    user,
    loading,
    isAuthenticated: Boolean(user),
    login,
    register,
    logout,
    refreshUser,
  }

  /**
   * Provides the authentication context to child components.
   */
  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  )
}