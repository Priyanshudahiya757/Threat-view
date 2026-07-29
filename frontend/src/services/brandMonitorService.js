import apiClient from './api'

export const listMonitors = () =>
  apiClient.get('/alerts/brand-monitors').then((r) => r.data)

export const createMonitor = (payload) =>
  apiClient.post('/alerts/brand-monitors', payload).then((r) => r.data)

export const deleteMonitor = (id) =>
  apiClient.delete(`/alerts/brand-monitors/${id}`).then((r) => r.data)
