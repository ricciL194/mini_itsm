# 前端登录页面详细设计

## 1. 页面概述

登录页面是用户进入系统的入口，包含：
- 登录表单（邮箱 + 密码）
- 注册入口
- 表单验证和错误提示
- 加载状态

## 2. UI 设计

### 2.1 布局结构

```
┌─────────────────────────────────────────────────┐
│                  [全屏背景]                      │
│                                                 │
│    ┌─────────────────────────────────────┐     │
│    │                                      │     │
│    │         ┌─────────────────┐          │     │
│    │         │   🔒 系统 Logo   │          │     │
│    │         └─────────────────┘          │     │
│    │                                      │     │
│    │         IT Service Desk              │     │
│    │         迷你工单管理系统               │     │
│    │                                      │     │
│    │    ┌────────────────────────────┐   │     │
│    │    │  📧  邮箱地址               │   │     │
│    │    └────────────────────────────┘   │     │
│    │                                      │     │
│    │    ┌────────────────────────────┐   │     │
│    │    │  🔒  密码            👁   │   │     │
│    │    └────────────────────────────┘   │     │
│    │                                      │     │
│    │    ┌────────────────────────────┐   │     │
│    │    │        登 录              │   │     │
│    │    └────────────────────────────┘   │     │
│    │                                      │     │
│    │       还没有账号？ [立即注册]          │     │
│    │                                      │     │
│    └─────────────────────────────────────┘     │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 2.2 设计规范

| 元素 | 规范 |
|------|------|
| 配色 | 主色 #409EFF (Element Plus Blue)，背景 #f0f2f5 |
| 卡片 | 白色背景，圆角 8px，阴影 `0 8px 32px rgba(0,0,0,0.1)` |
| 输入框 | 高度 48px，圆角 4px，边框 #dcdfe6 |
| 按钮 | 主色填充，高度 48px，圆角 4px |
| 响应式 | 移动端卡片宽度 90%，桌面端 400px |

### 2.3 组件状态

**输入框状态：**
- Default: 灰色边框 #dcdfe6
- Focus: 蓝色边框 #409EFF
- Error: 红色边框 #f56c6c
- Disabled: 灰色背景 #f5f7fa

**按钮状态：**
- Default: #409EFF 背景
- Hover: #66b1ff 背景
- Loading: 显示加载动画，禁用点击
- Disabled: #a0cfff 背景

## 3. Vue3 组件结构

### 3.1 文件结构

```
src/
├── views/
│   ├── LoginView.vue          # 登录页面
│   └── RegisterView.vue       # 注册页面
├── components/
│   └── auth/
│       ├── LoginForm.vue      # 登录表单组件
│       ├── RegisterForm.vue   # 注册表单组件
│       └── SocialLogin.vue    # 社交登录（预留）
├── stores/
│   └── auth.ts                # 认证状态管理
├── api/
│   └── auth.ts                # 认证 API 调用
└── router/
    └── index.ts               # 路由配置
```

### 3.2 LoginView.vue

```vue
<template>
  <div class="login-container">
    <div class="login-card">
      <!-- Logo 区域 -->
      <div class="login-header">
        <div class="logo">
          <svg class="logo-icon" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7l10 5 10-5-10-5z" stroke="currentColor" stroke-width="2"/>
            <path d="M2 17l10 5 10-5" stroke="currentColor" stroke-width="2"/>
            <path d="M2 12l10 5 10-5" stroke="currentColor" stroke-width="2"/>
          </svg>
        </div>
        <h1 class="title">IT Service Desk</h1>
        <p class="subtitle">迷你工单管理系统</p>
      </div>

      <!-- 登录表单 -->
      <LoginForm @success="onLoginSuccess" />

      <!-- 注册入口 -->
      <div class="login-footer">
        <span class="footer-text">还没有账号？</span>
        <router-link to="/register" class="register-link">
          立即注册
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LoginForm from '@/components/auth/LoginForm.vue'

const router = useRouter()
const authStore = useAuthStore()

const onLoginSuccess = () => {
  // 登录成功后跳转到首页或之前页面
  const redirect = router.currentRoute.value.query.redirect as string || '/'
  router.push(redirect)
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-icon {
  width: 64px;
  height: 64px;
  color: #409EFF;
}

.title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 16px 0 8px;
}

.subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.login-footer {
  margin-top: 24px;
  text-align: center;
}

.footer-text {
  color: #909399;
  font-size: 14px;
}

.register-link {
  color: #409EFF;
  text-decoration: none;
  margin-left: 4px;
  font-weight: 500;
}

.register-link:hover {
  text-decoration: underline;
}

@media (max-width: 480px) {
  .login-card {
    width: 90%;
    padding: 24px;
  }
}
</style>
```

### 3.3 LoginForm.vue

```vue
<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    class="login-form"
    @submit.prevent="handleLogin"
  >
    <!-- 邮箱 -->
    <el-form-item prop="email">
      <el-input
        v-model="form.email"
        placeholder="邮箱地址"
        size="large"
        :prefix-icon="Message"
        clearable
      />
    </el-form-item>

    <!-- 密码 -->
    <el-form-item prop="password">
      <el-input
        v-model="form.password"
        type="password"
        placeholder="密码"
        size="large"
        :prefix-icon="Lock"
        :suffix-icon="showPassword ? View : Hide"
        @click-suffix="showPassword = !showPassword"
        @keyup.enter="handleLogin"
        show-password
      />
    </el-form-item>

    <!-- 错误提示 -->
    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      show-icon
      :closable="false"
      class="error-alert"
    />

    <!-- 登录按钮 -->
    <el-form-item>
      <el-button
        type="primary"
        size="large"
        :loading="loading"
        class="login-button"
        native-type="submit"
      >
        {{ loading ? '登录中...' : '登 录' }}
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Message, Lock, View, Hide } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { login } from '@/api/auth'

const emit = defineEmits<{
  success: []
}>()

const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const errorMessage = ref('')
const showPassword = ref(false)

const form = reactive({
  email: '',
  password: ''
})

const rules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码至少 8 个字符', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    errorMessage.value = ''

    try {
      const response = await login({
        email: form.email,
        password: form.password
      })

      // 存储 Token
      authStore.setTokens(response.access_token, response.refresh_token)

      // 获取用户信息
      await authStore.fetchCurrentUser()

      emit('success')
    } catch (error: any) {
      errorMessage.value = error.response?.data?.detail || '登录失败，请稍后重试'
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-form {
  margin-top: 24px;
}

.login-button {
  width: 100%;
  margin-top: 8px;
}

.error-alert {
  margin-bottom: 16px;
}

:deep(.el-input__wrapper) {
  padding: 4px 16px;
}

:deep(.el-input__prefix) {
  color: #909399;
}
</style>
```

## 4. Pinia 状态管理

### 4.1 auth store (stores/auth.ts)

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { getCurrentUser, refreshToken as refreshTokenApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const currentUser = ref<User | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value && !!currentUser.value)
  const isAdmin = computed(() => currentUser.value?.role === 'admin')
  const userId = computed(() => currentUser.value?.id)

  // Actions
  const setTokens = (access: string, refresh: string) => {
    accessToken.value = access
    refreshToken.value = refresh

    // 可选：加密存储到 sessionStorage 作为备份
    if (typeof sessionStorage !== 'undefined') {
      sessionStorage.setItem('refresh_token', btoa(refresh))
    }
  }

  const setCurrentUser = (user: User) => {
    currentUser.value = user
  }

  const fetchCurrentUser = async () => {
    try {
      const user = await getCurrentUser()
      currentUser.value = user
    } catch (error) {
      // Token 可能已过期
      logout()
      throw error
    }
  }

  const refreshAccessToken = async (): Promise<string | null> => {
    if (!refreshToken.value) return null

    try {
      const response = await refreshTokenApi(refreshToken.value)
      accessToken.value = response.access_token
      refreshToken.value = response.refresh_token
      return response.access_token
    } catch (error) {
      logout()
      return null
    }
  }

  const logout = () => {
    accessToken.value = null
    refreshToken.value = null
    currentUser.value = null
    sessionStorage.removeItem('refresh_token')
  }

  // 从 sessionStorage 恢复 refresh token
  const restoreFromStorage = () => {
    const stored = sessionStorage.getItem('refresh_token')
    if (stored) {
      try {
        refreshToken.value = atob(stored)
      } catch {
        sessionStorage.removeItem('refresh_token')
      }
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
    // Actions
    setTokens,
    setCurrentUser,
    fetchCurrentUser,
    refreshAccessToken,
    logout,
    restoreFromStorage
  }
})
```

## 5. API 调用层

### 5.1 auth API (api/auth.ts)

```typescript
import axios from 'axios'
import type { AxiosInstance } from 'axios'
import { useAuthStore } from '@/stores/auth'

// 创建 axios 实例
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000
})

// 请求拦截器：附加 Token
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

// 响应拦截器：处理 401，自动刷新 Token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const authStore = useAuthStore()
    const originalRequest = error.config

    // 如果是 401 且不是刷新请求
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const newToken = await authStore.refreshAccessToken()
        if (newToken) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`
          return api(originalRequest)
        }
      } catch {
        // 刷新失败，跳转登录
        authStore.logout()
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

// ============ Auth API ============

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export const login = (data: LoginRequest): Promise<TokenResponse> =>
  api.post('/auth/login', data).then(res => res.data)

export const register = (data: RegisterRequest) =>
  api.post('/auth/register', data)

export const refreshToken = (refresh: string): Promise<TokenResponse> =>
  api.post('/auth/refresh', null, {
    headers: { Authorization: `Bearer ${refresh}` }
  }).then(res => res.data)

export const logout = () =>
  api.post('/auth/logout').then(res => res.data)

export const getCurrentUser = (): Promise<User> =>
  api.get('/auth/me').then(res => res.data)

export default api
```

## 6. 路由守卫

### 6.1 router/index.ts

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue')
      },
      {
        path: 'tickets',
        name: 'Tickets',
        component: () => import('@/views/TicketsView.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 如果需要认证
  if (to.meta.requiresAuth) {
    // 检查是否已登录
    if (!authStore.isAuthenticated) {
      // 尝试从存储恢复
      authStore.restoreFromStorage()

      if (authStore.refreshToken) {
        try {
          // 尝试刷新 Token
          await authStore.refreshAccessToken()
          await authStore.fetchCurrentUser()
          next()
        } catch {
          // 刷新失败，跳转登录
          next({ name: 'Login', query: { redirect: to.fullPath } })
        }
      } else {
        next({ name: 'Login', query: { redirect: to.fullPath } })
      }
    } else {
      next()
    }
  } else {
    // 已登录用户访问登录页，跳转首页
    if (to.name === 'Login' && authStore.isAuthenticated) {
      next({ name: 'Dashboard' })
    } else {
      next()
    }
  }
})

export default router
```

## 7. 交互流程图

```
┌──────────────────────────────────────────────────────────────┐
│                      用户登录流程                            │
└──────────────────────────────────────────────────────────────┘

  ┌─────────┐
  │  打开   │
  │ 登录页  │
  └────┬────┘
       │
       ▼
  ┌─────────────────┐
  │  输入邮箱密码    │◄─────────────────┐
  └────┬────────────┘                  │
       │                               │
       ▼                               │
  ┌─────────────────┐    验证失败      │
  │  前端表单验证   │─────────────────┼──► 显示错误提示
  └────┬────────────┘                  │
       │ 验证通过                      │
       ▼                               │
  ┌─────────────────┐                  │
  │  调用登录 API   │                  │
  └────┬────────────┘                  │
       │                               │
       ▼                               │
  ┌─────────────┐                      │
  │  API 返回   │                      │
  └─────┬───────┘                      │
        │                              │
   ┌────┴────┐                         │
   │ 成功？  │                         │
   └────┬────┘                         │
    是  │  否                          │
    │   │                              │
    ▼   └──► 显示 "Invalid credentials"│
  ┌─────────────────┐                 │
  │ 保存 Token 到   │                 │
  │ Pinia Store    │                 │
  └────┬────────────┘                 │
       │                              │
       ▼                              │
  ┌─────────────────┐                 │
  │ 调用 /auth/me   │                 │
  │ 获取用户信息    │                 │
  └────┬────────────┘                 │
       │                              │
       ▼                              │
  ┌─────────────────┐                 │
  │ 保存用户信息    │                 │
  │ 跳转首页/重定向 │─────────────────┘
  └─────────────────┘
```

## 8. 错误处理

| 错误类型 | 用户提示 | 处理方式 |
|----------|----------|----------|
| 网络错误 | "网络连接失败，请检查网络" | 显示重试按钮 |
| 401 凭据错误 | "邮箱或密码错误" | 清空密码输入框 |
| 403 账户禁用 | "账户已被禁用，请联系管理员" | 跳转错误页面 |
| 422 验证错误 | 显示具体字段错误 | 高亮对应输入框 |
| 500 服务器错误 | "服务器繁忙，请稍后重试" | 显示重试按钮 |

## 9. 国际化（可选）

```typescript
// locales/zh-CN.ts
export default {
  login: {
    title: 'IT Service Desk',
    subtitle: '迷你工单管理系统',
    email: '邮箱地址',
    password: '密码',
    loginButton: '登录',
    noAccount: '还没有账号？',
    registerLink: '立即注册',
    emailPlaceholder: '请输入邮箱',
    passwordPlaceholder: '请输入密码',
    errors: {
      emailRequired: '请输入邮箱地址',
      emailInvalid: '请输入有效的邮箱地址',
      passwordRequired: '请输入密码',
      passwordTooShort: '密码至少 8 个字符',
      invalidCredentials: '邮箱或密码错误',
      networkError: '网络连接失败，请检查网络',
      serverError: '服务器繁忙，请稍后重试'
    }
  }
}
```
