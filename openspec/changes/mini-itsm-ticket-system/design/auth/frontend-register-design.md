# 前端注册页面详细设计

## 1. 页面概述

注册页面用于新用户创建账户，包含：
- 用户名、邮箱、密码、确认密码表单
- 实时表单验证
- 密码强度指示
- 用户协议勾选（可选）
- 登录入口

## 2. UI 设计

### 2.1 布局结构

```
┌─────────────────────────────────────────────────┐
│                  [全屏背景]                      │
│                                                 │
│    ┌─────────────────────────────────────┐     │
│    │                                      │     │
│    │         ┌─────────────────┐          │     │
│    │         │   📝 系统 Logo   │          │     │
│    │         └─────────────────┘          │     │
│    │                                      │     │
│    │         创建账户                       │     │
│    │         加入工单管理系统                │     │
│    │                                      │     │
│    │    ┌────────────────────────────┐   │     │
│    │    │  👤  用户名               │   │     │
│    │    └────────────────────────────┘   │     │
│    │                                      │     │
│    │    ┌────────────────────────────┐   │     │
│    │    │  📧  邮箱地址             │   │     │
│    │    └────────────────────────────┘   │     │
│    │                                      │     │
│    │    ┌────────────────────────────┐   │     │
│    │    │  🔒  密码            👁   │   │     │
│    │    └────────────────────────────┘   │     │
│    │    [████░░░░░░] 中等               │   │
│    │                                      │     │
│    │    ┌────────────────────────────┐   │     │
│    │    │  🔒  确认密码          👁   │   │     │
│    │    └────────────────────────────┘   │     │
│    │                                      │     │
│    │    ☑️  我已阅读并同意《用户协议》      │     │
│    │                                      │     │
│    │    ┌────────────────────────────┐   │     │
│    │    │        注 册              │   │     │
│    │    └────────────────────────────┘   │     │
│    │                                      │     │
│    │       已有账号？ [立即登录]            │     │
│    │                                      │     │
│    └─────────────────────────────────────┘     │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 2.2 密码强度指示器

```
密码强度分级：

弱 (红色)    - 仅小写字母或仅数字，少于 8 字符
中等 (橙色)  - 8位以上，包含字母 + 数字
强 (绿色)    - 8位以上，包含大小写 + 数字
非常强 (绿色+图标) - 12位以上，大小写 + 数字 + 特殊字符

示例：
[████████░░] 强    ✓ 大小写字母 + 数字
[██████░░░░] 中等  ✓ 8位以上 + 字母 + 数字
[██░░░░░░░░] 弱    ✗ 密码强度不足
```

## 3. Vue3 组件结构

### 3.1 RegisterView.vue

```vue
<template>
  <div class="register-container">
    <div class="register-card">
      <!-- Logo 区域 -->
      <div class="register-header">
        <div class="logo">
          <svg class="logo-icon" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7l10 5 10-5-10-5z" stroke="currentColor" stroke-width="2"/>
            <path d="M2 17l10 5 10-5" stroke="currentColor" stroke-width="2"/>
            <path d="M2 12l10 5 10-5" stroke="currentColor" stroke-width="2"/>
          </svg>
        </div>
        <h1 class="title">创建账户</h1>
        <p class="subtitle">加入工单管理系统</p>
      </div>

      <!-- 注册表单 -->
      <RegisterForm @success="onRegisterSuccess" />

      <!-- 登录入口 -->
      <div class="register-footer">
        <span class="footer-text">已有账号？</span>
        <router-link to="/login" class="login-link">
          立即登录
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import RegisterForm from '@/components/auth/RegisterForm.vue'

const router = useRouter()

const onRegisterSuccess = () => {
  // 注册成功后跳转到登录页
  router.push('/login')
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-card {
  width: 420px;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.register-header {
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

.register-footer {
  margin-top: 24px;
  text-align: center;
}

.footer-text {
  color: #909399;
  font-size: 14px;
}

.login-link {
  color: #409EFF;
  text-decoration: none;
  margin-left: 4px;
  font-weight: 500;
}

.login-link:hover {
  text-decoration: underline;
}

@media (max-width: 480px) {
  .register-card {
    width: 90%;
    padding: 24px;
  }
}
</style>
```

### 3.2 RegisterForm.vue

```vue
<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    class="register-form"
    @submit.prevent="handleRegister"
  >
    <!-- 用户名 -->
    <el-form-item prop="username">
      <el-input
        v-model="form.username"
        placeholder="用户名"
        size="large"
        :prefix-icon="User"
        clearable
        maxlength="50"
        show-word-limit
      />
    </el-form-item>

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
        placeholder="密码（至少 8 位）"
        size="large"
        :prefix-icon="Lock"
        show-password
        @input="handlePasswordInput"
      />
      <!-- 密码强度指示器 -->
      <PasswordStrength :password="form.password" class="password-strength" />
    </el-form-item>

    <!-- 确认密码 -->
    <el-form-item prop="confirmPassword">
      <el-input
        v-model="form.confirmPassword"
        type="password"
        placeholder="确认密码"
        size="large"
        :prefix-icon="Lock"
        show-password
      />
    </el-form-item>

    <!-- 用户协议 -->
    <el-form-item prop="agreeTerms">
      <el-checkbox v-model="form.agreeTerms">
        我已阅读并同意
        <el-link type="primary" :underline="false">《用户协议》</el-link>
        和
        <el-link type="primary" :underline="false">《隐私政策》</el-link>
      </el-checkbox>
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

    <!-- 注册按钮 -->
    <el-form-item>
      <el-button
        type="primary"
        size="large"
        :loading="loading"
        :disabled="!form.agreeTerms"
        class="register-button"
        native-type="submit"
      >
        {{ loading ? '注册中...' : '注 册' }}
      </el-button>
    </el-form-item>

    <!-- 成功提示 -->
    <el-result
      v-if="success"
      icon="success"
      title="注册成功"
      sub-title="即将跳转到登录页面..."
      class="success-result"
    />
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { User, Message, Lock } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { register } from '@/api/auth'
import PasswordStrength from './PasswordStrength.vue'

const emit = defineEmits<{
  success: []
}>()

const formRef = ref<FormInstance>()
const loading = ref(false)
const errorMessage = ref('')
const success = ref(false)

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreeTerms: false
})

// 自定义验证：确认密码
const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度 2-50 个字符', trigger: 'blur' },
    {
      pattern: /^[a-zA-Z0-9_\u4e00-\u9fa5]+$/,
      message: '用户名只能包含字母、数字、下划线和中文',
      trigger: 'blur'
    }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码至少 8 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  agreeTerms: [
    {
      validator: (rule, value, callback) => {
        if (!value) {
          callback(new Error('请阅读并同意用户协议'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

// 密码输入时清除确认密码的错误状态
const handlePasswordInput = () => {
  if (form.confirmPassword) {
    formRef.value?.validateField('confirmPassword')
  }
}

const handleRegister = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    errorMessage.value = ''

    try {
      await register({
        username: form.username,
        email: form.email,
        password: form.password
      })

      success.value = true

      // 3 秒后跳转登录页
      setTimeout(() => {
        emit('success')
      }, 3000)
    } catch (error: any) {
      const detail = error.response?.data?.detail

      // 处理后端返回的具体错误
      if (detail === 'Email already registered') {
        errorMessage.value = '该邮箱已被注册'
        formRef.value?.setFieldError('email', '该邮箱已被注册')
      } else if (detail === 'Username already taken') {
        errorMessage.value = '该用户名已被使用'
        formRef.value?.setFieldError('username', '该用户名已被使用')
      } else {
        errorMessage.value = '注册失败，请稍后重试'
      }
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.register-form {
  margin-top: 24px;
}

.register-button {
  width: 100%;
  margin-top: 8px;
}

.error-alert {
  margin-bottom: 16px;
}

.password-strength {
  margin-top: 8px;
}

.success-result {
  padding: 20px 0;
}

:deep(.el-input__wrapper) {
  padding: 4px 16px;
}

:deep(.el-input__prefix) {
  color: #909399;
}

:deep(.el-checkbox__label) {
  font-size: 13px;
  color: #606266;
}
</style>
```

### 3.3 PasswordStrength.vue（密码强度组件）

```vue
<template>
  <div v-if="password" class="password-strength">
    <div class="strength-bar">
      <div
        class="strength-fill"
        :class="strengthClass"
        :style="{ width: barWidth }"
      />
    </div>
    <span class="strength-text" :class="strengthClass">
      {{ strengthLabel }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  password: string
}>()

// 密码强度计算
const passwordStrength = computed(() => {
  const pwd = props.password
  if (!pwd) return { score: 0, level: 'none' }

  let score = 0
  const checks = {
    length: pwd.length >= 8,
    length12: pwd.length >= 12,
    lowercase: /[a-z]/.test(pwd),
    uppercase: /[A-Z]/.test(pwd),
    number: /[0-9]/.test(pwd),
    special: /[^a-zA-Z0-9]/.test(pwd)
  }

  // 基础分数
  if (checks.length) score += 1
  if (checks.length12) score += 1

  // 字符类型分数
  if (checks.lowercase) score += 1
  if (checks.uppercase) score += 1
  if (checks.number) score += 1
  if (checks.special) score += 1

  // 转换为等级
  if (score <= 2) return { score: 33, level: 'weak' }
  if (score <= 4) return { score: 66, level: 'medium' }
  if (score <= 5) return { score: 80, level: 'strong' }
  return { score: 100, level: 'very-strong' }
})

const barWidth = computed(() => `${passwordStrength.value.score}%`)

const strengthClass = computed(() => passwordStrength.value.level)

const strengthLabel = computed(() => {
  const labels = {
    weak: '弱 - 建议使用更强密码',
    medium: '中等 - 可以更安全',
    strong: '强',
    'very-strong': '非常强'
  }
  return labels[passwordStrength.value.level]
})
</script>

<style scoped>
.password-strength {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.strength-bar {
  flex: 1;
  height: 4px;
  background: #e4e7ed;
  border-radius: 2px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  transition: all 0.3s ease;
  border-radius: 2px;
}

.strength-text {
  font-size: 12px;
  min-width: 100px;
}

.strength-fill.weak,
.strength-text.weak {
  background: #f56c6c;
  color: #f56c6c;
}

.strength-fill.medium,
.strength-text.medium {
  background: #e6a23c;
  color: #e6a23c;
}

.strength-fill.strong,
.strength-text.strong {
  background: #67c23a;
  color: #67c23a;
}

.strength-fill.very-strong,
.strength-text.very-strong {
  background: #409eff;
  color: #409eff;
}
</style>
```

## 4. API 调用

### 4.1 api/auth.ts 新增

```typescript
// ============ Register API ============

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface RegisterResponse {
  id: string
  username: string
  email: string
  message: string
}

export const register = (data: RegisterRequest): Promise<RegisterResponse> =>
  api.post('/auth/register', data).then(res => res.data)
```

## 5. 交互流程图

```
┌──────────────────────────────────────────────────────────────┐
│                      用户注册流程                            │
└──────────────────────────────────────────────────────────────┘

  ┌─────────┐
  │  打开   │
  │ 注册页  │
  └────┬────┘
       │
       ▼
  ┌─────────────────┐
  │  输入用户信息    │◄──────────────────┐
  └────┬────────────┘                   │
       │                                │
       ▼                                │
  ┌─────────────────┐   验证失败        │
  │  实时表单验证   │──────────────────┼──► 显示具体字段错误
  └────┬────────────┘                   │
       │ 验证通过                       │
       ▼                                │
  ┌─────────────────┐                   │
  │  勾选用户协议   │ 未勾选             │
  └────┬────────────┘──────────────────┼──► 禁用注册按钮
       │ 已勾选                        │
       ▼                                │
  ┌─────────────────┐                   │
  │  点击注册按钮   │                   │
  └────┬────────────┘                   │
       │                                │
       ▼                                │
  ┌─────────────────┐                   │
  │  调用注册 API   │                   │
  └────┬────────────┘                   │
       │                                │
       ▼                                │
  ┌─────────────┐                       │
  │  API 返回   │                       │
  └─────┬───────┘                       │
        │                               │
   ┌────┴────┐                          │
   │ 成功？  │                          │
   └────┬────┘                          │
    是  │  否                           │
    │   │                               │
    ▼   └──► 显示错误消息                │
  ┌─────────────────┐                  │
  │ 显示成功结果    │                  │
  │ 3秒后跳转登录  │──────────────────┘
  └─────────────────┘
```

## 6. 验证规则汇总

| 字段 | 规则 | 错误提示 |
|------|------|----------|
| 用户名 | 必填 | 请输入用户名 |
| 用户名 | 2-50 字符 | 用户名长度 2-50 个字符 |
| 用户名 | 格式正则 | 用户名只能包含字母、数字、下划线和中文 |
| 邮箱 | 必填 | 请输入邮箱地址 |
| 邮箱 | 邮箱格式 | 请输入有效的邮箱地址 |
| 邮箱 | 唯一性 | 该邮箱已被注册 |
| 密码 | 必填 | 请输入密码 |
| 密码 | 最少 8 位 | 密码至少 8 个字符 |
| 确认密码 | 必填 | 请确认密码 |
| 确认密码 | 与密码一致 | 两次输入的密码不一致 |
| 用户协议 | 必选 | 请阅读并同意用户协议 |

## 7. 密码强度计算规则

```
评分标准：

基础分 (0-2分):
- 长度 >= 8: +1分
- 长度 >= 12: +1分

字符类型 (0-4分):
- 包含小写字母: +1分
- 包含大写字母: +1分
- 包含数字: +1分
- 包含特殊字符: +1分

最终等级:
- 0-2分: 弱 (红色)
- 3-4分: 中等 (橙色)
- 5分: 强 (绿色)
- 6分: 非常强 (蓝色)
```

## 8. 错误处理

| 场景 | 后端返回 | 前端处理 |
|------|----------|----------|
| 邮箱已注册 | `{"detail": "Email already registered"}` | 高亮邮箱输入框，显示 "该邮箱已被注册" |
| 用户名已被使用 | `{"detail": "Username already taken"}` | 高亮用户名输入框，显示 "该用户名已被使用" |
| 密码不符合要求 | HTTP 422 | Pydantic 验证错误，显示具体要求 |
| 网络错误 | - | 显示 "网络连接失败，请检查网络" |
| 服务器错误 | HTTP 500 | 显示 "服务器繁忙，请稍后重试" |

## 9. 注册成功页设计

```vue
<!-- 注册成功提示（替代表单显示） -->
<template>
  <div class="success-container">
    <el-result
      icon="success"
      title="注册成功"
      sub-title="您的账户已创建成功，3 秒后跳转到登录页面..."
    >
      <template #extra>
        <el-button type="primary" @click="goToLogin">
          立即登录
        </el-button>
      </template>
    </el-result>

    <!-- 倒计时指示 -->
    <div class="countdown">
      <el-progress
        :percentage="percentage"
        :show-text="false"
        :stroke-width="4"
        color="#67c23a"
      />
      <span class="countdown-text">{{ countdown }} 秒后自动跳转</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const totalSeconds = 3
const currentSecond = ref(totalSeconds)

const percentage = computed(() =>
  ((totalSeconds - currentSecond.value) / totalSeconds) * 100
)

const countdown = computed(() => totalSeconds - currentSecond.value + 1)

onMounted(() => {
  const timer = setInterval(() => {
    currentSecond.value--
    if (currentSecond.value <= 0) {
      clearInterval(timer)
      router.push('/login')
    }
  }, 1000)
})

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.success-container {
  text-align: center;
  padding: 40px 0;
}

.countdown {
  margin-top: 24px;
  max-width: 200px;
  margin-left: auto;
  margin-right: auto;
}

.countdown-text {
  display: block;
  margin-top: 8px;
  font-size: 13px;
  color: #909399;
}
</style>
```

## 10. 国际化（可选）

```typescript
// locales/zh-CN.ts
export default {
  register: {
    title: '创建账户',
    subtitle: '加入工单管理系统',
    username: '用户名',
    email: '邮箱地址',
    password: '密码',
    confirmPassword: '确认密码',
    passwordPlaceholder: '密码（至少 8 位）',
    agreeTerms: '我已阅读并同意《用户协议》和《隐私政策》',
    registerButton: '注册',
    successTitle: '注册成功',
    successSubtitle: '即将跳转到登录页面',
    goToLogin: '立即登录',
    noAccount: '已有账号？',
    errors: {
      usernameRequired: '请输入用户名',
      usernameLength: '用户名长度 2-50 个字符',
      usernameInvalid: '用户名只能包含字母、数字、下划线和中文',
      emailRequired: '请输入邮箱地址',
      emailInvalid: '请输入有效的邮箱地址',
      emailTaken: '该邮箱已被注册',
      passwordRequired: '请输入密码',
      passwordTooShort: '密码至少 8 个字符',
      confirmPasswordRequired: '请确认密码',
      passwordMismatch: '两次输入的密码不一致',
      termsRequired: '请阅读并同意用户协议',
      networkError: '网络连接失败，请检查网络',
      serverError: '服务器繁忙，请稍后重试'
    },
    strength: {
      weak: '弱 - 建议使用更强密码',
      medium: '中等 - 可以更安全',
      strong: '强',
      veryStrong: '非常强'
    }
  }
}
```
