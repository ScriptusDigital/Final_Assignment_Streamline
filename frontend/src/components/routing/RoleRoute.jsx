
/**
 * RoleRoute component to handle role-based routing.
 */

import {
    Navigate,
    Outlet,
} from 'react-router'


/* 
Check if the user is authenticated and has the required role.
*/
import { useAuth } from '../../contexts/useAuth'


/**
 * RoleRoute component implementation.
 */

export function RoleRoute({ allowedRoles }) {
    const { user, loading, isAuthenticated, } = useAuth()

    if (loading) {
        return (
            <p role="status">Loading...</p>
        )
    }

    if (!isAuthenticated) {
        return (
            <Navigate
                to="/login"
                replace
            />
        )
    }

    if (!allowedRoles.includes(user?.role)) {
        return (
            <Navigate
                to="/dashboard" replace />

        )
    }

    return <Outlet />
}