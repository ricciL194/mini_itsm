<template>
  <div class="login-container">
    <div class="login-card">
      <!-- Logo 区域 -->
      <div class="login-header">
        <div class="logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>
        </div>
        <h1 class="title">IT Service Desk</h1>
        <p class="subtitle">迷你工单管理系统</p>
      </div>

      <!-- 登录表单 -->
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
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
            placeholder="密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
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
            class="login-button"
            native-type="submit"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 注册入口 -->
      <div class="login-footer">
        <span class="footer-text">还没有账号？</span>
        <router-link to="/register" class="register-link">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Message, Lock } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const errorMessage = ref('')

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
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    errorMessage.value = ''

    try {
      await authStore.login(form.email, form.password)
      ElMessage.success('登录成功')

      const redirect = router.currentRoute.value.query.redirect as string || '/'
      router.push(redirect)
    } catch (error: any) {
      const detail = error.response?.data?.detail
      if (detail === '账户已被禁用') {
        errorMessage.value = '账户已被禁用，请联系管理员'
      } else {
        errorMessage.value = '邮箱或密码错误'
      }
    } finally {
      loading.value = false
    }
  })
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
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.login-header {
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

.login-form {
  margin-top: 24px;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
}

.error-alert {
  margin-bottom: 16px;
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
