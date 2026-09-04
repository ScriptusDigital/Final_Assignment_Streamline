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