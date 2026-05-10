import axios from 'axios'
import { getAccessToken, removeTokens, getRefreshToken, setTokens } from './auth'

const api = axios.create({
  baseURL: 'http://127.0.0.1:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

let isRefreshing = false
let failedQueue = []

function processQueue(error, token = null) {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

api.interceptors.request.use(
  (config) => {
    const token = getAccessToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then(token => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return api(originalRequest)
          })
          .catch(err => Promise.reject(err))
      }
      
      originalRequest._retry = true
      isRefreshing = true
      
      try {
        const refreshToken = getRefreshToken()
        if (!refreshToken) {
          throw new Error('No refresh token')
        }
        
        const response = await api.post('/auth/refresh', {
          refresh_token: refreshToken
        })
        
        const { access_token, refresh_token } = response.data
        setTokens(access_token, refresh_token)
        
        originalRequest.headers.Authorization = `Bearer ${access_token}`
        
        processQueue(null, access_token)
        
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        removeTokens()
        
        if (typeof window !== 'undefined') {
          window.location.href = '/login'
        }
        
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }
    
    return Promise.reject(error)
  }
)

export default api