import { useState } from 'react'
import {
  Link,
  Navigate,
  useNavigate,
} from 'react-router'

import { ApiError } from '../api/client'
import { useAuth } from '../contexts/useAuth'
import '../styles/auth.css'
function getRegistrationErrorMessage(error) {
  if (
    error instanceof ApiError &&
    error.data &&
    typeof error.data === 'object'
  ) {
    const firstMessage = Object
      .values(error.data)
      .flat()
      .find((message) => (
        typeof message === 'string'
      ))

    if (firstMessage) {
      return firstMessage
    }

    return error.message
  }

  return 'Unable to create your account. Please try again.'
}
