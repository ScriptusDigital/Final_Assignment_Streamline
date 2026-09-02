const API_BASE = import.meta.env.VITE_API_BASE ?? '/api'

const SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']

function readCookie(name) {
  const prefix = `${encodeURIComponent(name)}=`

const cookie = document.cookie
    .split('; ')
    .find((item) => item.startsWith(prefix))

  if (!cookie) {
    return null
  }

  return decodeURIComponent(cookie.slice(prefix.length))
}

function getErrorMessage(data, status) {