import {
    Navigate, Outlet,
} from "react-router-dom";

import { useAuth } from "../../context/useAuth"

export function RoleRoute({ allowedRoles }) {
    const {user, loading, isAuthenticated,} = useAuth()

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