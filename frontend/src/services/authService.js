import apiClient from './api'

export const login = (email, password) =>
  apiClient.post('/auth/login', { email, password }).then((r) => r.data)

export const register = (payload) =>
  apiClient.post('/auth/register', payload).then((r) => r.data)

export const refreshToken = (refreshTok) =>
  apiClient
    .post('/auth/refresh', {}, { headers: { Authorization: `Bearer ${refreshTok}` } })
    .then((r) => r.data)

export const getMe = () =>
  apiClient.get('/auth/me').then((r) => r.data)
