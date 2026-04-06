<template>
  <div class="audit-view">
    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="操作类型">
          <el-select v-model="filterForm.action" placeholder="全部操作" clearable style="width: 160px">
            <el-option
              v-for="action in ACTION_OPTIONS"
              :key="action.value"
              :label="action.label"
              :value="action.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="资源类型">
          <el-select v-model="filterForm.resource_type" placeholder="全部资源" clearable style="width: 140px">
            <el-option label="工单" value="ticket" />
            <el-option label="用户" value="user" />
            <el-option label="认证" value="auth" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 日志列表 -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <span>审计日志（共 {{ pagination.total }} 条）</span>
      </template>

      <el-table :data="logs" stripe v-loading="loading">
        <el-table-column prop="created_at" label="时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="action" label="操作" width="180">
          <template #default="{ row }">
            <el-tag size="small">{{ getActionLabel(row.action) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resource_type" label="资源类型" width="100">
          <template #default="{ row }">
            <span>{{ getResourceLabel(row.resource_type) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="resource_id" label="资源ID" width="220">
          <template #default="{ row }">
            <span v-if="row.resource_id" class="mono">{{ row.resource_id.slice(0, 16) }}...</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="130">
          <template #default="{ row }">
            {{ row.ip_address || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="变更内容" min-width="200">
          <template #default="{ row }">
            <div v-if="row.old_value || row.new_value" class="change-detail">
              <span v-if="row.old_value && row.new_value" class="change-field">
                <span class="old">{{ formatChange(row.old_value) }}</span>
                <span class="arrow"> → </span>
                <span class="new">{{ formatChange(row.new_value) }}</span>
              </span>
              <span v-else-if="row.new_value" class="change-field">
                <span class="new">{{ formatChange(row.new_value) }}</span>
              </span>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.limit"
          :total="pagination.total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { auditApi } from '@/api/audit'
import type { AuditLog } from '@/types'

const loading = ref(false)
const logs = ref<AuditLog[]>([])

const filterForm = reactive({ action: '', resource_type: '' })

const pagination = reactive({ page: 1, limit: 20, total: 0 })

const ACTION_OPTIONS = [
  { label: '全部操作', value: '' },
  { label: '登录', value: 'auth.login' },
  { label: '注册', value: 'auth.register' },
  { label: '登出', value: 'auth.logout' },
  { label: '创建工单', value: 'ticket.create' },
  { label: '更新工单', value: 'ticket.update' },
  { label: '删除工单', value: 'ticket.delete' },
  { label: '指派工单', value: 'ticket.assign' },
  { label: '取消指派', value: 'ticket.unassign' },
  { label: '变更状态', value: 'ticket.status_change' },
  { label: '更新用户', value: 'user.update' },
]

const ACTION_LABELS: Record<string, string> = {
  'auth.login': '登录',
  'auth.register': '注册',
  'auth.logout': '登出',
  'ticket.create': '创建工单',
  'ticket.update': '更新工单',
  'ticket.delete': '删除工单',
  'ticket.assign': '指派工单',
  'ticket.unassign': '取消指派',
  'ticket.status_change': '变更状态',
  'user.update': '更新用户',
}

const getActionLabel = (action: string) => ACTION_LABELS[action] || action
const getResourceLabel = (rt: string) => ({ ticket: '工单', user: '用户', auth: '认证' }[rt] || rt)

const formatDate = (d: string) =>
  new Date(d).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })

const formatChange = (val: Record<string, any> | null) => {
  if (!val) return ''
  return Object.entries(val)
    .map(([k, v]) => `${k}: ${v}`)
    .join(', ')
}

const fetchLogs = async () => {
  loading.value = true
  try {
    const res = await auditApi.getLogs({
      action: filterForm.action || undefined,
      resource_type: filterForm.resource_type || undefined,
      page: pagination.page,
      limit: pagination.limit
    })
    logs.value = res.items
    pagination.total = res.total
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '加载审计日志失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => { pagination.page = 1; fetchLogs() }
const handleReset = () => { filterForm.action = ''; filterForm.resource_type = ''; handleSearch() }
const handleSizeChange = () => { pagination.page = 1; fetchLogs() }
const handlePageChange = () => { fetchLogs() }

onMounted(() => { fetchLogs() })
</script>

<style scoped>
.audit-view {
  max-width: 1400px;
  margin: 0 auto;
}

.filter-card {
  margin-bottom: 16px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.mono {
  font-family: monospace;
  font-size: 11px;
  color: #909399;
}

.change-detail {
  font-size: 12px;
  line-height: 1.6;
}

.old {
  color: #f56c6c;
  text-decoration: line-through;
}

.arrow {
  color: #909399;
}

.new {
  color: #67c23a;
}
</style>
