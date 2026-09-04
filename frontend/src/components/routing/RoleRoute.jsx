import {
    Navigate, Outlet,
} from "react-router-dom";

import { useAuth } from "../../context/useAuth"

export function RoleRoute({ allowedRoles }) {
    const { user } = useAuth();

    if (!user) {
        return <Navigate to="/login" />;
    }

    if (!allowedRoles.includes(user.role)) {
        return <Navigate to="/unauthorized" />;
    }

    return <Outlet />;
}