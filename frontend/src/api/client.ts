import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '',
  timeout: 30_000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  r => r,
  error => {
    const msg = error.response?.data?.detail ?? error.message
    console.error('[API Error]', msg)
    return Promise.reject(error)
  }
)
