import apiClient from './api'

export const getHealth = () => apiClient.get('/health').then((res) => res.data)

export const getThreats = (params = {}) => apiClient.get('/threats', { params }).then((res) => res.data)

export const getThreatById = (id) => apiClient.get(`/threats/${id}`).then((res) => res.data)

export const getStats = () => apiClient.get('/stats').then((res) => res.data)

export const getMalwareTrendsTimeseries = (days = 14, topN = 6) =>
  apiClient.get('/stats/malware-trends-timeseries', { params: { days, top_n: topN } }).then((res) => res.data)

export const searchThreats = (q, params = {}) =>
  apiClient.get('/search', { params: { q, ...params } }).then((res) => res.data)

export const getRecentThreats = (limit = 20) => apiClient.get('/recent', { params: { limit } }).then((res) => res.data)
