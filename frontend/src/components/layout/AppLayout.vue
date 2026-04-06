<template>
  <div class="app-layout" :class="{ 'sidebar-hover': sidebarHovered }">
    <!-- 侧边栏：默认收起，hover 展开 -->
    <div
      class="sidebar"
      @mouseenter="sidebarHovered = true"
      @mouseleave="sidebarHovered = false"
    >
      <!-- Logo -->
      <div class="logo-area">
        <svg class="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5z"/>
          <path d="M2 17l10 5 10-5"/>
          <path d="M2 12l10 5 10-5"/>
        </svg>
        <span class="logo-text">Mini ITSM</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="!sidebarHovered"
        :collapse-transition="false"
        class="sidebar-menu"
        router
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>

        <el-menu-item index="/tickets">
          <el-icon><Tickets /></el-icon>
          <template #title>工单列表</template>
        </el-menu-item>

        <el-menu-item index="/tickets/create">
          <el-icon><Plus /></el-icon>
          <template #title>创建工单</template>
        </el-menu-item>

        <el-menu-item v-if="authStore.isAdmin" index="/users">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>

        <el-menu-item v-if="authStore.isAdmin" index="/audit">
          <el-icon><Document /></el-icon>
          <template #title>审计日志</template>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- 主内容 -->
    <div class="main-wrapper">
      <!-- 顶部栏 -->
      <header class="header">
        <div class="header-left">
          <h2 class="page-title">{{ currentTitle }}</h2>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" :icon="UserFilled" />
              <span class="username">{{ authStore.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 内容区 -->
      <main class="main-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  HomeFilled,
  Tickets,
  Plus,
  User,
  Document,
  UserFilled,
  ArrowDown,
  SwitchButton
} from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const sidebarHovered = ref(false)

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta.title as string || '首页')

const handleCommand = async (command: string) => {
  if (command === 'logout') {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await authStore.logout()
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
/* 根容器 */
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* ========== 侧边栏 ========== */
.sidebar {
  position: relative;
  height: 100vh;
  width: 64px;               /* 收起宽度 */
  min-width: 64px;
  background: #304156;
  overflow: hidden;
  transition: width 0.25s ease;
  z-index: 100;
  flex-shrink: 0;
}

.app-layout.sidebar-hover .sidebar {
  width: 220px;               /* 展开宽度 */
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 16px;
  height: 60px;
  border-bottom: 1px solid #3d4a5c;
  overflow: hidden;
  white-space: nowrap;
}

.logo-icon {
  width: 28px;
  height: 28px;
  color: #409EFF;
  flex-shrink: 0;
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  opacity: 0;
  transition: opacity 0.2s 0.1s;
}

.app-layout.sidebar-hover .logo-text {
  opacity: 1;
}

.sidebar-menu {
  border-right: none !important;
  background: transparent !important;
  width: 100%;
}

:deep(.el-menu--collapse) {
  width: 64px !important;
}

:deep(.el-menu-item) {
  color: #bfcbd9;
  padding-left: 20px !important;
  height: 50px;
  line-height: 50px;
  overflow: hidden;
  white-space: nowrap;
}

:deep(.el-menu-item .el-icon) {
  font-size: 18px;
  flex-shrink: 0;
}

:deep(.el-menu-item:hover) {
  background: #263445;
  color: #409EFF;
}

:deep(.el-menu-item.is-active) {
  background: #263445;
  color: #409EFF;
}

/* ========== 主内容区 ========== */
.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  padding: 0 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background 0.3s;
}

.user-info:hover {
  background: #f5f7fa;
}

.username {
  font-size: 14px;
  color: #606266;
}

.main-content {
  flex: 1;
  background: #f5f7fa;
  padding: 24px;
  overflow-y: auto;
}
</style>
