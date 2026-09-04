
/**
 * Custom hook for accessing authentication context.
 */

import { useContext } from 'react'
import { AuthContext } from './auth-context'

export function useAuth() {
const context = useContext(AuthContext)

if (!context) {
  throw new Error('useAuth must be used within an AuthProvider')
}

return context
}

return context