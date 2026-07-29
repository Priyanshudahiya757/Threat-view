import apiClient from './api'

// ── Alert Rules ──────────────────────────────────────────────────────────────

export const listRules = (activeOnly = false) =>
  apiClient.get('/alerts/rules', { params: { active_only: activeOnly } }).then((r) => r.data)

export const createRule = (payload) =>
  apiClient.post('/alerts/rules', payload).then((r) => r.data)

export const updateRule = (id, payload) =>
  apiClient.put(`/alerts/rules/${id}`, payload).then((r) => r.data)

export const deleteRule = (id) =>
  apiClient.delete(`/alerts/rules/${id}`).then((r) => r.data)

// ── Alert Events ─────────────────────────────────────────────────────────────

export const listEvents = ({ page = 1, perPage = 20, unreadOnly = false } = {}) =>
  apiClient
    .get('/alerts/events', { params: { page, per_page: perPage, unread_only: unreadOnly } })
    .then((r) => r.data)

export const markEventRead = (id) =>
  apiClient.post(`/alerts/events/${id}/read`).then((r) => r.data)

export const markAllRead = () =>
  apiClient.post('/alerts/events/read-all').then((r) => r.data)

export const getUnreadCount = () =>
  apiClient.get('/alerts/notifications/unread-count').then((r) => r.data.unread_count)
