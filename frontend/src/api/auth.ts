import api from './client'
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  RegisterResponse,
  User
} from '@/types'

// 认证 API
export const authApi = {
  // 登录
  login: (data: LoginRequest): Promise<TokenResponse> =>
    api.post('/auth/login', data).then(res => res.data),

  // 注册
  register: (data: RegisterRequest): Promise<RegisterResponse> =>
    api.post('/auth/register', data).then(res => res.data),

  // 刷新 Token
  refresh: (refreshToken: string): Promise<TokenResponse> =>
    api.post('/auth/refresh', null, {
      headers: { Authorization: `Bearer ${refreshToken}` }
    }).then(res => res.data),

  // 登出
  logout: (refreshToken?: string) => api.post('/auth/logout', { refresh_token: refreshToken }).then(res => res.data),

  // 获取当前用户
  getCurrentUser: (): Promise<User> =>
    api.get('/auth/me').then(res => res.data)
}
