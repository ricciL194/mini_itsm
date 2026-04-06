import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const currentUser = ref<User | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value && !!currentUser.value)
  const isAdmin = computed(() => currentUser.value?.role === 'admin')
  const userId = computed(() => currentUser.value?.id)
  const username = computed(() => currentUser.value?.username)

  // Actions
  const setTokens = (access: string, refresh: string) => {
    accessToken.value = access
    refreshToken.value = refresh

    // 加密存储到 sessionStorage 作为备份
    if (typeof sessionStorage !== 'undefined') {
      try {
        sessionStorage.setItem('refresh_token', btoa(refresh))
      } catch {
        // 忽略存储错误
      }
    }
  }

  const setUser = (user: User) => {
    currentUser.value = user
  }

  const login = async (email: string, password: string) => {
    const response = await authApi.login({ email, password })
    setTokens(response.access_token, response.refresh_token)
    await fetchCurrentUser()
  }

  const register = async (username: string, email: string, password: string) => {
    return authApi.register({ username, email, password })
  }

  const fetchCurrentUser = async () => {
    try {
      const user = await authApi.getCurrentUser()
      setUser(user)
      return user
    } catch (error) {
      logout()
      throw error
    }
  }

  const doRefreshToken = async (): Promise<string | null> => {
    if (!refreshToken.value) return null

    try {
      const response = await authApi.refresh(refreshToken.value)
      setTokens(response.access_token, response.refresh_token)
      return response.access_token
    } catch (error) {
      logout()
      return null
    }
  }

  const logout = async () => {
    try {
      await authApi.logout(refreshToken.value ?? undefined)
    } catch {
      // 忽略登出错误
    }

    accessToken.value = null
    refreshToken.value = null
    currentUser.value = null
    sessionStorage.removeItem('refresh_token')
  }

  // 从 sessionStorage 恢复
  const restoreFromStorage = () => {
    try {
      const stored = sessionStorage.getItem('refresh_token')
      if (stored) {
        refreshToken.value = atob(stored)
      }
    } catch {
      sessionStorage.removeItem('refresh_token')
    }
  }

  return {
    // State
    accessToken,
    refreshToken,
    currentUser,
    // Getters
    isAuthenticated,
    isAdmin,
    userId,
    username,
    // Actions
    setTokens,
    setUser,
    login,
    register,
    fetchCurrentUser,
    doRefreshToken,
    logout,
    restoreFromStorage
  }
})
