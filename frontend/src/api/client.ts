import axios from 'axios'
import type { AxiosInstance } from 'axios'
import { useAuthStore } from '@/stores/auth'

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const authStore = useAuthStore()
    const originalRequest = error.config

    // 401 处理：尝试刷新 Token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      if (authStore.refreshToken) {
        try {
          const newToken = await authStore.doRefreshToken()
          if (newToken) {
            originalRequest.headers.Authorization = `Bearer ${newToken}`
            return api(originalRequest)
          }
        } catch {
          authStore.logout()
        }
      }

      // 刷新失败，跳转登录
      authStore.logout()
    }

    return Promise.reject(error)
  }
)

export default api
