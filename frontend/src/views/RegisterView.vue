<template>
  <div class="register-container">
    <div class="register-card">
      <!-- Logo 区域 -->
      <div class="register-header">
        <div class="logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>
        </div>
        <h1 class="title">创建账户</h1>
        <p class="subtitle">加入工单管理系统</p>
      </div>

      <!-- 注册表单 -->
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="register-form"
        @submit.prevent="handleRegister"
      >
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

        <el-form-item prop="email">
          <el-input
            v-model="form.email"
            placeholder="邮箱地址"
            size="large"
            :prefix-icon="Message"
            clearable
          />
        </el-form-item>

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
          <div v-if="form.password" class="password-strength">
            <div class="strength-bar">
              <div
                class="strength-fill"
                :class="strengthClass"
                :style="{ width: barWidth }"
              />
            </div>
            <span class="strength-text" :class="strengthClass">{{ strengthLabel }}</span>
          </div>
        </el-form-item>

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

        <el-form-item prop="agreeTerms">
          <el-checkbox v-model="form.agreeTerms">
            我已阅读并同意
            <el-link type="primary" :underline="false">《用户协议》</el-link>
            和
            <el-link type="primary" :underline="false">《隐私政策》</el-link>
          </el-checkbox>
        </el-form-item>

        <el-alert
          v-if="errorMessage"
          :title="errorMessage"
          type="error"
          show-icon
          :closable="false"
          class="error-alert"
        />

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
      </el-form>

      <!-- 登录入口 -->
      <div class="register-footer">
        <span class="footer-text">已有账号？</span>
        <router-link to="/login" class="login-link">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Message, Lock } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const errorMessage = ref('')

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreeTerms: false
})

// 密码强度计算
const passwordStrength = computed(() => {
  const pwd = form.password
  if (!pwd) return { score: 0, level: 'none' }

  let score = 0
  if (pwd.length >= 8) score += 1
  if (pwd.length >= 12) score += 1
  if (/[a-z]/.test(pwd)) score += 1
  if (/[A-Z]/.test(pwd)) score += 1
  if (/[0-9]/.test(pwd)) score += 1
  if (/[^a-zA-Z0-9]/.test(pwd)) score += 1

  if (score <= 2) return { score: 33, level: 'weak' }
  if (score <= 4) return { score: 66, level: 'medium' }
  if (score <= 5) return { score: 80, level: 'strong' }
  return { score: 100, level: 'very-strong' }
})

const barWidth = computed(() => `${passwordStrength.value.score}%`)
const strengthClass = computed(() => passwordStrength.value.level)
const strengthLabel = computed(() => {
  const labels: Record<string, string> = {
    weak: '弱',
    medium: '中等',
    strong: '强',
    'very-strong': '非常强'
  }
  return labels[passwordStrength.value.level] || ''
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
    { min: 2, max: 50, message: '用户名长度 2-50 个字符', trigger: 'blur' }
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
  ]
}

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
      await authStore.register(form.username, form.email, form.password)
      ElMessage.success('注册成功，请登录')
      router.push('/login')
    } catch (error: any) {
      const detail = error.response?.data?.detail
      if (detail === '该邮箱已被注册') {
        errorMessage.value = '该邮箱已被注册'
        formRef.value?.setFieldError('email', '该邮箱已被注册')
      } else if (detail === '该用户名已被使用') {
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
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  width: 64px;
  height: 64px;
  margin: 0 auto;
  color: #409EFF;
}

.logo svg {
  width: 100%;
  height: 100%;
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

.register-form {
  margin-top: 24px;
}

.register-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
}

.error-alert {
  margin-bottom: 16px;
}

.password-strength {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
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

.strength-fill.weak { background: #f56c6c; }
.strength-fill.medium { background: #e6a23c; }
.strength-fill.strong { background: #67c23a; }
.strength-fill.very-strong { background: #409eff; }

.strength-text {
  font-size: 12px;
  min-width: 40px;
}
.strength-text.weak { color: #f56c6c; }
.strength-text.medium { color: #e6a23c; }
.strength-text.strong { color: #67c23a; }
.strength-text.very-strong { color: #409eff; }

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
