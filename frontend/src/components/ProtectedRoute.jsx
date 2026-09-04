/**
 *  Protect routes from unauthenticated access.
 * Redirects to the login page if the user is not authenticated.
 */


import {
    Navigate,
    Outlet, useLocation,
} from 'react-router'

import { useAuth } from '../contexts/useAuth.js'

export