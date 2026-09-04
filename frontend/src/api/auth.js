
/**
 * Authentication API functions
 */

import { apiRequest } from './client';

export function initialiseCsrf() {
  return apiRequest('/auth/csrf/')
}

export function getCurrentUser() {
  return apiRequest('/auth/me/')
}

export function loginUser(credentials) {
  return apiRequest('/auth/login/', {
    method: 'POST',
    body: credentials,
  })
}

export function registerUser(details) {
  return apiRequest('/auth/register/', {
    method: 'POST',
    body: details,
  })
}


export function logoutUser() {
  return apiRequest('/auth/logout/', {
    method: 'POST',
  })
}