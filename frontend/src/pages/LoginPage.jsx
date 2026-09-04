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
        login,
        isAuthenticated,
    } = useAuth()

    /** React Router hooks for navigation and location */
    const location = useLocation()
    const navigate = useNavigate()

    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [formError, setFormError] = useState('')
    const [submitting, setSubmitting] =
        useState(false)

    const previousLocation =
        location.state?.from

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
    /** Form submission handler */
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
  /
    return (
        <main>
            <section aria-labelledby="login-heading">
                <p>Streamline</p>

                <h1 id="login-heading">
                    Log in
                </h1>

                <form onSubmit={handleSubmit}>
                    <div>
                        <label htmlFor="email">
                            Email address
                        </label>

                        <input id="email"
                            name="email"
                            type="email"
                            autoComplete="email"
                            required
                            value={email}
                            onChange={(event) => {
                                setEmail(event.target.value)
                            }}
                        />
                    </div>

                    <div>
                        <label htmlFor="password">
                            Password
                        </label>

                        <input
                            id="password"
                            name="password"
                            type="password"
                            autoComplete="current-password"
                            required
                            value={password}
                            onChange={(event) => {
                                setPassword(event.target.value)
                            }}
                        /></div>

                    {formError && (
                        <p role="alert">
                            {formError}
                        </p>
                    )}

                    <button
                        type="submit"
                        disabled={submitting}
                    >
                        {submitting
                            ? 'Logging in…'
                            : 'Log in'}
                    </button>
                </form>

                <p>
                    No account yet?{' '}
                    <Link to="/register">
                        Create one
                    </Link>
                </p>
            </section>
        </main>
    )
}