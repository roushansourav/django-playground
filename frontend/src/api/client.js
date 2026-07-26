const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'

function getAccessToken() {
  return localStorage.getItem('accessToken')
}

export async function apiFetch(path, options = {}) {
  const token = getAccessToken()
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }
  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers })
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed with status ${response.status}`)
  }
  if (response.status === 204) {
    return null
  }
  return response.json()
}

export { API_BASE_URL, getAccessToken }
