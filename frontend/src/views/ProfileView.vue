<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>个人信息</span>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="用户ID">
          {{ authStore.currentUser?.id }}
        </el-descriptions-item>
        <el-descriptions-item label="用户名">
          {{ authStore.currentUser?.username }}
        </el-descriptions-item>
        <el-descriptions-item label="邮箱">
          {{ authStore.currentUser?.email }}
        </el-descriptions-item>
        <el-descriptions-item label="角色">
          <el-tag :type="authStore.isAdmin ? 'danger' : 'success'" size="small">
            {{ authStore.isAdmin ? '管理员' : '普通用户' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="账户状态">
          <el-tag :type="authStore.currentUser?.is_active ? 'success' : 'danger'" size="small">
            {{ authStore.currentUser?.is_active ? '正常' : '已禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="注册时间">
          {{ formatDate(authStore.currentUser?.created_at) }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 0 auto;
}

.profile-card {
  margin-bottom: 24px;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
}
</style>
