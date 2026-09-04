/**
 * LoginPage imports for handling user login.
 */

import { useState } from 'react'
import {
    Link, Navigate, useLocation, useNavigate,
}
    from 'react-router';


import { ApiError } from '../api/client'
import { useAuth } from '../contexts/useAuth'


/**
 * Login error message.
 */
function getLoginErrorMessage(error) {
    if (error instanceof ApiError) {
        const backendMessages =
            error.data?.non_field_errors

        if (
            Array.isArray(backendMessages) &&
            backendMessages.length > 0
        ) {
            return backendMessages[0]
        }

        return error.message
    }
    return 'Unable to log in. Please try again'
}

/* LoginPage elemenst */

export function LoginPage() {
    const {
        login, isAuthenticated,
    } = useAuth()

    const location = useLocation()
    const navigate = useNavigate()

    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [formError, setFormError] = useState('')
    const [submitting, setSubmitting] =
        useState(false)


    const previousLocation = 
    location.state?.formError


  const destination =
    previousLocation?.pathname ??
    '/dashboard'

  if (isAuthenticated) {
    return (
      <Navigate
        to="/dashboard"
        replace
      />
    )
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setFormError('')
    setSubmitting(true)

    try {
      await login({
        email,
        password,
      })

      navigate(destination, {
        replace: true,
      })
    } catch (error) {
      setFormError(
        getLoginErrorMessage(error),
      )
    } finally {
      setSubmitting(false)
    }
  }

