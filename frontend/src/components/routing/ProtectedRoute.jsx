/**
 *  Protect routes from unauthenticated access.
 * Redirects to the login page if the user is not authenticated.
 */


import {
    Navigate,
    Outlet, useLocation,
} from 'react-router'

import { useAuth } from '../../contexts/useAuth'

/**
 * ProtectedRoute component implementation.
 */

export function ProtectedRoute() {
    const {loading, isAuthenticated} = useAuth()

    const location = useLocation()

    if (loading) {
      return (
        <p role="status">Loading Streamline...</p>
      )
    }
    
    if (!isAuthenticated) {
        return <Navigate to="/login" replace state  ={{ from: location }} />
    }

    return <Outlet />
}