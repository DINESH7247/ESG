import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
})

export const uploadData = async (formData) => {
  const { data } = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export const fetchRecords = async (params = {}) => {
  const { data } = await api.get('/records', { params })
  return data.results || []
}

export const fetchRecord = async (id) => {
  const { data } = await api.get(`/records/${id}`)
  return data
}

export const updateReview = async (id, payload) => {
  const { data } = await api.patch(`/records/${id}/review`, payload)
  return data
}

export const fetchAuditLogs = async (recordId) => {
  const { data } = await api.get(`/audit-logs/${recordId}`)
  return data.results || []
}
