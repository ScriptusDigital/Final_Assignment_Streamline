
/**
 * Client API functions, including request handling and error management.
 */

const API_BASE = import.meta.env.VITE_API_BASE ?? '/api'

const SAFE_METHODS = new Set([
  'GET',
  'HEAD',
  'OPTIONS',
])

function readCookie(name) {
  const prefix = `${encodeURIComponent(name)}=`

  const cookie = document.cookie
    .split('; ')
    .find((item) => item.startsWith(prefix))

  if (!cookie) {
    return null
  }

  return decodeURIComponent(
    cookie.slice(prefix.length),
  )
}

function getErrorMessage(data, status) {
  if (
    data &&
    typeof data === 'object' &&
    typeof data.detail === 'string'
  ) {
    return data.detail
  }

  return `Request failed with status ${status}.`
}

export class ApiError extends Error {
  constructor(message, status, data) {
    super(message)

    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

export async function apiRequest(
  path,
  options = {},
) {
  const method = (
    options.method ?? 'GET'
  ).toUpperCase()

  const headers = new Headers(options.headers)
  let body = options.body

  headers.set('Accept', 'application/json')

  const isFormData = body instanceof FormData

  if (
    body !== undefined &&
    body !== null &&
    !isFormData &&
    typeof body !== 'string'
  ) {
    headers.set(
      'Content-Type',
      'application/json',
    )

    body = JSON.stringify(body)
  }

  if (!SAFE_METHODS.has(method)) {
    const csrfToken = readCookie('csrftoken')

    if (csrfToken) {
      headers.set('X-CSRFToken', csrfToken)
    }
  }

  const response = await fetch(
    `${API_BASE}${path}`,
    {
      ...options,
      method,
      headers,
      body,
      credentials: 'include',
    },
  )

  const contentType =
    response.headers.get('content-type') ?? ''

  const responseText = (
    response.status === 204
      ? ''
      : await response.text()
  )

  const data = (
    responseText &&
    contentType.includes('application/json')
      ? JSON.parse(responseText)
      : responseText || null
  )

  if (!response.ok) {
    throw new ApiError(
      getErrorMessage(data, response.status),
      response.status,
      data,
    )
  }

  return data
}