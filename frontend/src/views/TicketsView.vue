<template>
  <div class="tickets-view">
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="in_progress" />
            <el-option label="已解决" value="resolved" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="filterForm.priority" placeholder="全部优先级" clearable>
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="tickets-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>工单列表</span>
          <el-button type="primary" @click="router.push('/tickets/create')">
            <el-icon><Plus /></el-icon>
            创建工单
          </el-button>
        </div>
      </template>

      <el-table :data="tickets" stripe v-loading="loading">
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
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="router.push(`/tickets/${row.id}`)">
              查看
            </el-button>
            <el-button
              v-if="canEdit(row)"
              type="primary"
              text
              size="small"
              @click="router.push(`/tickets/${row.id}/edit`)"
            >
              编辑
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.limit"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { ticketApi } from '@/api/ticket'
import type { Ticket } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)

const filterForm = reactive({
  status: '',
  priority: ''
})

const pagination = reactive({
  page: 1,
  limit: 20,
  total: 0
})

// 静态演示数据
const tickets = ref<Ticket[]>([])

const fetchTickets = async () => {
  loading.value = true
  try {
    const response = await ticketApi.getTickets({
      status: filterForm.status || undefined,
      priority: filterForm.priority || undefined,
      page: pagination.page,
      limit: pagination.limit
    })
    tickets.value = response.items
    pagination.total = response.total
  } catch {
    tickets.value = []
  } finally {
    loading.value = false
  }
}

// 工具函数
const getPriorityType = (priority: string) => {
  const map: Record<string, string> = { high: 'danger', medium: 'warning', low: 'info' }
  return map[priority] || 'info'
}

const getPriorityLabel = (priority: string) => {
  const map: Record<string, string> = { high: '高', medium: '中', low: '低' }
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

const canEdit = (ticket: Ticket) => {
  return ticket.creator.id === authStore.userId || authStore.isAdmin
}

const handleSearch = () => {
  pagination.page = 1
  fetchTickets()
}

const handleReset = () => {
  filterForm.status = ''
  filterForm.priority = ''
  handleSearch()
}

const handleSizeChange = (_size: number) => {
  pagination.page = 1
  fetchTickets()
}

const handlePageChange = (page: number) => {
  pagination.page = page
  fetchTickets()
}

onMounted(() => {
  fetchTickets()
})
</script>

<style scoped>
.tickets-view {
  max-width: 1400px;
  margin: 0 auto;
}

.filter-card {
  margin-bottom: 16px;
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

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
