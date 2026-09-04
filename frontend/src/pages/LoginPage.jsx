/**
 * LoginPage imports for handling user login.
 */

import { useState } from 'react'
import {
    Link,
    Navigate,
    useLocation,
    useNavigate,
} from 'react-router';

import { ApiError } from '../api/client'
import { useAuth } from '../contexts/useAuth'
import '../styles/auth.css'

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
    return (
        <main className="auth-page">
            <section
                className="auth-card"
                aria-labelledby="login-heading"
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
                <h1 id="login-heading">
                    Welcome back
                </h1>

                <p className="auth-intro">
                    Log in to manage, review and find
                    your photography.
                </p>

                <form
                    className="auth-form"
                    onSubmit={handleSubmit}
                >
                    <div className="form-field">
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

                    <div className="form-field">
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
                        className="auth-submit"
                        type="submit"
                        disabled={submitting}
                    >
                        {submitting
                            ? 'Logging in…'
                            : 'Log in'}
                    </button>
                </form>

                <p className="auth-switch">
                    No account yet?{' '}
                    <Link to="/register">
                        Create one
                    </Link>
                </p>
            </section>
        </main>
    )
}