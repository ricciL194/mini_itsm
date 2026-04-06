<template>
  <div class="dashboard">
    <!-- 欢迎卡片 -->
    <el-card class="welcome-card" shadow="hover">
      <div class="welcome-content">
        <div class="welcome-text">
          <h2>欢迎回来，{{ authStore.username }}！</h2>
          <p>今天是 {{ currentDate }}，祝您工作愉快！</p>
        </div>
        <div class="quick-actions">
          <el-button type="primary" @click="router.push('/tickets/create')">
            <el-icon><Plus /></el-icon>
            创建工单
          </el-button>
          <el-button @click="router.push('/tickets')">
            <el-icon><Tickets /></el-icon>
            查看工单
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon total">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.total }}</span>
          <span class="stat-label">工单总数</span>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon pending">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.pending }}</span>
          <span class="stat-label">待处理</span>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon in-progress">
          <el-icon><Loading /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.in_progress }}</span>
          <span class="stat-label">处理中</span>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon resolved">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.resolved }}</span>
          <span class="stat-label">已解决</span>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon closed">
          <el-icon><Check /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.closed }}</span>
          <span class="stat-label">已关闭</span>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon my">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.my }}</span>
          <span class="stat-label">我的工单</span>
        </div>
      </el-card>
    </div>

    <!-- 最近工单 -->
    <el-card class="recent-tickets" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>最近工单</span>
          <el-button type="primary" text @click="router.push('/tickets')">
            查看全部 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </template>

      <el-table :data="recentTickets" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="{ row }">
            <router-link :to="`/tickets/${row.id}`" class="ticket-link">
              {{ row.title }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">
              {{ getPriorityLabel(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="creator.username" label="创建人" width="120" />
        <el-table-column prop="assignee" label="指派给" width="120">
          <template #default="{ row }">
            {{ row.assignee?.username || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 快捷操作 -->
    <el-card class="quick-links" shadow="hover">
      <template #header>
        <span>快捷操作</span>
      </template>
      <div class="links-grid">
        <div class="quick-link-item" @click="router.push('/tickets/create')">
          <div class="link-icon create">
            <el-icon><Plus /></el-icon>
          </div>
          <span>创建工单</span>
        </div>
        <div class="quick-link-item" @click="router.push('/tickets?status=pending')">
          <div class="link-icon pending">
            <el-icon><Clock /></el-icon>
          </div>
          <span>待处理工单</span>
        </div>
        <div class="quick-link-item" @click="router.push('/tickets?assignee=me')">
          <div class="link-icon assigned">
            <el-icon><User /></el-icon>
          </div>
          <span>我的指派</span>
        </div>
        <div class="quick-link-item" @click="router.push('/tickets?creator=me')">
          <div class="link-icon created">
            <el-icon><Document /></el-icon>
          </div>
          <span>我创建的</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Plus, Tickets, Document, Clock, Loading, CircleCheck, Check, User, ArrowRight } from '@element-plus/icons-vue'
import { ticketApi } from '@/api/ticket'
import type { Ticket } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

// 当前日期
const currentDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
  weekday: 'long'
})

// 统计数据（从 API 加载）
const stats = ref({ total: 0, pending: 0, in_progress: 0, resolved: 0, closed: 0, my: 0 })

// 最近工单
const recentTickets = ref<Ticket[]>([])
const loading = ref(false)

const fetchDashboard = async () => {
  loading.value = true
  try {
    // 并行请求：全部工单 + 我的工单
    const [allRes, myRes] = await Promise.all([
      ticketApi.getTickets({ limit: 100 }),
      ticketApi.getTickets({ assignee_id: authStore.userId ?? undefined, limit: 100 })
    ])

    // 统计各项数量
    const all = allRes.items
    stats.value = {
      total: allRes.total,
      pending: all.filter(t => t.status === 'pending').length,
      in_progress: all.filter(t => t.status === 'in_progress').length,
      resolved: all.filter(t => t.status === 'resolved').length,
      closed: all.filter(t => t.status === 'closed').length,
      my: myRes.total
    }

    // 最近 5 条
    recentTickets.value = all.slice(0, 5)
  } catch {
    // 静默失败，保留空数据
  } finally {
    loading.value = false
  }
}

// 工具函数
const getPriorityType = (priority: string) => {
  const map: Record<string, string> = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return map[priority] || 'info'
}

const getPriorityLabel = (priority: string) => {
  const map: Record<string, string> = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return map[priority] || priority
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'warning',
    in_progress: 'primary',
    resolved: 'success',
    closed: 'info'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    pending: '待处理',
    in_progress: '处理中',
    resolved: '已解决',
    closed: '已关闭'
  }
  return map[status] || status
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchDashboard()
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.welcome-card {
  margin-bottom: 24px;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-text h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #303133;
}

.welcome-text p {
  margin: 0;
  color: #909399;
}

.quick-actions {
  display: flex;
  gap: 12px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.total { background: #ecf5ff; color: #409EFF; }
.stat-icon.pending { background: #fdf6ec; color: #e6a23c; }
.stat-icon.in-progress { background: #f0f9ff; color: #1890ff; }
.stat-icon.resolved { background: #f6ffed; color: #52c41a; }
.stat-icon.closed { background: #f9f9f9; color: #8c8c8c; }
.stat-icon.my { background: #fff0f6; color: #eb2f96; }

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

.recent-tickets {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ticket-link {
  color: #409EFF;
  text-decoration: none;
}

.ticket-link:hover {
  text-decoration: underline;
}

.quick-links {
  margin-bottom: 24px;
}

.links-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
}

.quick-link-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-link-item:hover {
  background: #ecf5ff;
  transform: translateY(-2px);
}

.link-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.link-icon.create { background: #409EFF; color: white; }
.link-icon.pending { background: #e6a23c; color: white; }
.link-icon.assigned { background: #1890ff; color: white; }
.link-icon.created { background: #52c41a; color: white; }

.quick-link-item span {
  font-size: 13px;
  color: #606266;
}
</style>
