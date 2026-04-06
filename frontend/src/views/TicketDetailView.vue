<template>
  <div class="ticket-detail-view" v-loading="loading">
    <!-- 找不到工单 -->
    <el-empty v-if="!loading && !ticket" description="工单不存在或无权访问" />

    <div v-else-if="ticket" class="detail-layout">
      <!-- 左侧：工单信息 -->
      <div class="main-content">
        <!-- 工单头 -->
        <el-card class="header-card" shadow="hover">
          <div class="ticket-header">
            <div class="title-row">
              <h1 class="ticket-title">{{ ticket.title }}</h1>
              <el-tag :type="getPriorityType(ticket.priority)" size="large">
                {{ getPriorityLabel(ticket.priority) }}
              </el-tag>
              <el-tag :type="getStatusType(ticket.status)" size="large">
                {{ getStatusLabel(ticket.status) }}
              </el-tag>
            </div>
            <div class="meta-row">
              <span>创建于 {{ formatDate(ticket.created_at) }}</span>
              <span v-if="ticket.updated_at !== ticket.created_at">
                · 更新于 {{ formatDate(ticket.updated_at) }}
              </span>
            </div>
          </div>
        </el-card>

        <!-- 描述 -->
        <el-card class="desc-card" shadow="hover">
          <template #header><span>描述</span></template>
          <div class="description">{{ ticket.description }}</div>
        </el-card>

        <!-- 状态历史 -->
        <el-card class="history-card" shadow="hover">
          <template #header>
            <span>状态变更历史</span>
          </template>
          <el-timeline v-if="ticket.status_history.length">
            <el-timeline-item
              v-for="item in ticket.status_history"
              :key="item.id"
              :type="getTimelineColor(item.to_status)"
              :timestamp="formatDate(item.created_at)"
              placement="top"
            >
              <div class="history-item">
                <span class="history-status">
                  {{ item.from_status ? `${getStatusLabel(item.from_status)} → ` : '' }}
                  {{ getStatusLabel(item.to_status) }}
                </span>
                <span class="history-user">由 {{ item.changed_by.username }} 变更</span>
              </div>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无变更记录" :image-size="60" />
        </el-card>
      </div>

      <!-- 右侧：操作面板 -->
      <div class="sidebar">
        <!-- 基本信息 -->
        <el-card class="info-card" shadow="hover">
          <template #header><span>基本信息</span></template>
          <div class="info-list">
            <div class="info-row">
              <span class="info-label">工单编号</span>
              <span class="info-value mono">{{ ticket.id }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">创建人</span>
              <span class="info-value">{{ ticket.creator.username }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">当前指派</span>
              <span class="info-value">{{ ticket.assignee?.username || '未指派' }}</span>
            </div>
          </div>
        </el-card>

        <!-- 变更状态 -->
        <el-card class="action-card" shadow="hover">
          <template #header><span>变更状态</span></template>
          <div class="status-buttons">
            <el-button
              v-for="next in allowedNextStatuses"
              :key="next"
              :type="getStatusButtonType(next)"
              @click="handleChangeStatus(next)"
              :loading="statusLoading"
            >
              {{ getStatusLabel(next) }}
            </el-button>
            <span v-if="!allowedNextStatuses.length" class="no-transition">
              当前状态不可变更
            </span>
          </div>
        </el-card>

        <!-- 指派处理人 -->
        <el-card class="action-card" shadow="hover">
          <template #header><span>指派处理人</span></template>
          <div class="assign-section">
            <el-select
              v-model="selectedAssignee"
              placeholder="选择处理人"
              clearable
              filterable
              :loading="usersLoading"
              @change="handleAssign"
              :disabled="assignLoading"
            >
              <el-option
                v-for="user in users"
                :key="user.id"
                :label="user.username"
                :value="user.id"
              />
            </el-select>
            <el-button
              v-if="selectedAssignee"
              type="primary"
              :loading="assignLoading"
              @click="handleAssign"
              style="margin-left: 8px"
            >
              确认
            </el-button>
          </div>
        </el-card>

        <!-- 操作按钮 -->
        <el-card class="action-card" shadow="hover">
          <template #header><span>操作</span></template>
          <div class="action-buttons">
            <el-button type="primary" @click="router.push(`/tickets/${ticket.id}/edit`)">
              编辑工单
            </el-button>
            <el-button
              v-if="canDelete"
              type="danger"
              plain
              @click="handleDelete"
              :loading="deleteLoading"
            >
              删除工单
            </el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ticketApi } from '@/api/ticket'
import { userApi } from '@/api/user'
import { useAuthStore } from '@/stores/auth'
import type { TicketDetail } from '@/types'
import type { UserBrief } from '@/api/user'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const ticket = ref<TicketDetail | null>(null)
const loading = ref(false)
const statusLoading = ref(false)
const assignLoading = ref(false)
const deleteLoading = ref(false)
const usersLoading = ref(false)
const users = ref<UserBrief[]>([])
const selectedAssignee = ref<string | null>(null)

const ticketId = computed(() => route.params.id as string)

// 允许的状态转换
const STATUS_TRANSITIONS: Record<string, string[]> = {
  pending: ['in_progress', 'closed'],
  in_progress: ['resolved', 'pending'],
  resolved: ['closed', 'in_progress'],
  closed: [],
}

const allowedNextStatuses = computed(() => {
  if (!ticket.value) return []
  return STATUS_TRANSITIONS[ticket.value.status] || []
})

const canDelete = computed(() => {
  if (!ticket.value) return false
  return ticket.value.creator.id === authStore.userId || authStore.isAdmin
})

// 工具函数
const getPriorityType = (p: string) =>
  ({ high: 'danger', medium: 'warning', low: 'info' }[p] || 'info')

const getPriorityLabel = (p: string) =>
  ({ high: '高', medium: '中', low: '低' }[p] || p)

const getStatusType = (s: string) =>
  ({ pending: 'warning', in_progress: 'primary', resolved: 'success', closed: 'info' }[s] || 'info')

const getStatusLabel = (s: string) =>
  ({
    pending: '待处理',
    in_progress: '处理中',
    resolved: '已解决',
    closed: '已关闭'
  }[s] || s)

const getStatusButtonType = (s: string) =>
  ({ pending: 'warning', in_progress: 'primary', resolved: 'success', closed: 'info' }[s] || 'primary')

const getTimelineColor = (s: string) =>
  ({ pending: 'warning', in_progress: 'primary', resolved: 'success', closed: 'info' }[s] || 'primary')

const formatDate = (d: string) => {
  return new Date(d).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

const fetchTicket = async () => {
  loading.value = true
  try {
    ticket.value = await ticketApi.getTicket(ticketId.value)
    selectedAssignee.value = ticket.value.assignee?.id ?? null
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '加载工单失败')
    ticket.value = null
  } finally {
    loading.value = false
  }
}

const fetchUsers = async () => {
  usersLoading.value = true
  try {
    users.value = await userApi.getUsers()
  } catch {
    users.value = []
  } finally {
    usersLoading.value = false
  }
}

const handleChangeStatus = async (nextStatus: string) => {
  statusLoading.value = true
  try {
    const updated = await ticketApi.changeStatus(ticketId.value, { status: nextStatus as any })
    if (ticket.value) {
      ticket.value.status = updated.status
      // 刷新完整详情（含历史）
      await fetchTicket()
    }
    ElMessage.success(`状态已变更为：${getStatusLabel(nextStatus)}`)
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '状态变更失败')
  } finally {
    statusLoading.value = false
  }
}

const handleAssign = async () => {
  if (!selectedAssignee.value && selectedAssignee.value !== null) return
  assignLoading.value = true
  try {
    const updated = await ticketApi.assignTicket(ticketId.value, { assignee_id: selectedAssignee.value })
    if (ticket.value) {
      ticket.value.assignee = updated.assignee
    }
    ElMessage.success(selectedAssignee.value ? '已指派处理人' : '已取消指派')
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '指派失败')
  } finally {
    assignLoading.value = false
  }
}

const handleDelete = async () => {
  try {
    await ElMessageBox.confirm('确定要删除此工单吗？此操作不可恢复。', '删除确认', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    })
  } catch {
    return
  }

  deleteLoading.value = true
  try {
    await ticketApi.deleteTicket(ticketId.value)
    ElMessage.success('工单已删除')
    router.push('/tickets')
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '删除失败')
  } finally {
    deleteLoading.value = false
  }
}

onMounted(() => {
  fetchTicket()
  fetchUsers()
})
</script>

<style scoped>
.ticket-detail-view {
  max-width: 1200px;
  margin: 0 auto;
}

.detail-layout {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.main-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sidebar {
  width: 280px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ticket-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.ticket-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.meta-row {
  font-size: 13px;
  color: #909399;
}

.description {
  white-space: pre-wrap;
  line-height: 1.7;
  color: #606266;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.info-label {
  font-size: 13px;
  color: #909399;
  flex-shrink: 0;
}

.info-value {
  font-size: 13px;
  color: #303133;
  text-align: right;
}

.mono {
  font-family: monospace;
  font-size: 11px;
}

.status-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.no-transition {
  font-size: 13px;
  color: #c0c4cc;
}

.assign-section {
  display: flex;
  align-items: center;
}

.assign-section .el-select {
  flex: 1;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.history-status {
  font-size: 14px;
  color: #303133;
}

.history-user {
  font-size: 12px;
  color: #909399;
}
</style>
