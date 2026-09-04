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

export function RegisterPage() {
  const {
    register,
    isAuthenticated,
  } = useAuth()

  const navigate = useNavigate()

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
  })

  const [formError, setFormError] = useState('')
  const [submitting, setSubmitting] =
    useState(false)

  if (isAuthenticated) {
    return (
      <Navigate
        to="/dashboard"
        replace
      />
    )
  }

  function handleChange(event) {
    const {
      name,
      value,
    } = event.target

    setFormData((currentData) => ({
      ...currentData,
      [name]: value,
    }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setFormError('')
    setSubmitting(true)

    try {
      await register(formData)

      navigate('/dashboard', {
        replace: true,
      })
    } catch (error) {
      setFormError(
        getRegistrationErrorMessage(error),
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="auth-page">
      <section
        className="auth-card"
        aria-labelledby="register-heading"
      >
        <Link
          to="/"
          className="auth-brand"
        >
          Streamline
        </Link>

        <p className="auth-kicker">
          Secure digital asset management
        </p>

        <h1 id="register-heading">
          Create an account
        </h1>

        <p className="auth-intro">
          New accounts begin with Viewer
          access.
        </p>

        <form
          className="auth-form"
          onSubmit={handleSubmit}
        >
          <div className="form-field">
            <label htmlFor="first_name">
              First name
            </label>

            <input
              id="first_name"
              name="first_name"
              type="text"
              autoComplete="given-name"
              required
              value={formData.first_name}
              onChange={handleChange}
            />
          </div>

          <div className="form-field">
            <label htmlFor="last_name">
              Last name
            </label>

            <input
              id="last_name"
              name="last_name"
              type="text"
              autoComplete="family-name"
              required
              value={formData.last_name}
              onChange={handleChange}
            />
          </div>

          <div className="form-field">
            <label htmlFor="email">
              Email address
            </label>

            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={formData.email}
              onChange={handleChange}
            />
          </div>

          <div className="form-field">
            <label htmlFor="password">
              Password
            </label>

            <input
              id="password"
              name="password"
              type="password"
              autoComplete="new-password"
              required
              value={formData.password}
              onChange={handleChange}
            />
          </div>

          {formError && (
            <p role="alert">
              {formError}
            </p>
          )}

          <button
            className="auth-submit"
            type="submit"
            disabled={submitting}
          >
            {submitting
              ? 'Creating account…'
              : 'Create account'}
          </button>
        </form>

        <p className="auth-switch">
          Already registered?{' '}
          <Link to="/login">
            Log in
          </Link>
        </p>
      </section>
    </main>
  )
}