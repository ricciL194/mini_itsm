import api from './client'

export interface UserBrief {
  id: string
  username: string
}

export interface UserInfo {
  id: string
  username: string
  email: string
  role: 'admin' | 'user'
  is_active: boolean
  created_at: string
}

export interface UpdateUserRequest {
  role?: 'admin' | 'user'
  is_active?: boolean
}

export interface CreateUserRequest {
  username: string
  email: string
  password: string
  role?: 'admin' | 'user'
}

export const userApi = {
  getUsers: (): Promise<UserBrief[]> =>
    api.get('/users').then(res => res.data),

  getAllUsers: (): Promise<UserInfo[]> =>
    api.get('/users/all').then(res => res.data),

  createUser: (data: CreateUserRequest): Promise<UserInfo> =>
    api.post('/users', data).then(res => res.data),

  updateUser: (id: string, data: UpdateUserRequest): Promise<UserInfo> =>
    api.put(`/users/${id}`, data).then(res => res.data),
}
