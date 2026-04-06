<template>
  <div class="users-view" v-loading="loading">
    <el-card class="header-card" shadow="never">
      <div class="card-header">
        <span>用户列表</span>
        <el-button type="primary" @click="handleCreateUser">
          <el-icon><Plus /></el-icon>
          新建用户
        </el-button>
      </div>
    </el-card>

    <el-card class="table-card" shadow="hover">
      <el-table :data="users" stripe>
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'" size="small">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              text
              size="small"
              @click="openEditDialog(row)"
              :disabled="row.id === currentUserId"
            >
              编辑
            </el-button>
            <el-button
              :type="row.is_active ? 'warning' : 'success'"
              text
              size="small"
              @click="toggleStatus(row)"
              :loading="toggling === row.id"
              :disabled="row.id === currentUserId"
            >
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog v-model="dialogVisible" title="编辑用户" width="400px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" disabled />
        </el-form-item>
        <el-form-item label="角色">
          <el-radio-group v-model="editForm.role">
            <el-radio value="user">普通用户</el-radio>
            <el-radio value="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="editForm.is_active"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 新建用户对话框 -->
    <el-dialog v-model="createDialogVisible" title="新建用户" width="400px">
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="createForm.username" placeholder="2-50个字符" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="createForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="createForm.password" type="password" placeholder="至少8位" show-password />
        </el-form-item>
        <el-form-item label="角色">
          <el-radio-group v-model="createForm.role">
            <el-radio value="user">普通用户</el-radio>
            <el-radio value="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { userApi, type UserInfo } from '@/api/user'
import { useAuthStore } from '@/stores/auth'
import type { FormInstance, FormRules } from 'element-plus'

const authStore = useAuthStore()
const currentUserId = computed(() => authStore.userId ?? '')

const loading = ref(false)
const users = ref<UserInfo[]>([])
const toggling = ref<string | null>(null)

// 编辑
const dialogVisible = ref(false)
const saving = ref(false)
const editForm = reactive({ id: '', username: '', email: '', role: 'user' as 'admin' | 'user', is_active: true })

// 新建
const createDialogVisible = ref(false)
const creating = ref(false)
const createFormRef = ref<FormInstance>()
const createForm = reactive({ username: '', email: '', password: '', role: 'user' as 'admin' | 'user' })
const createRules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 8, message: '密码至少8位', trigger: 'blur' }]
}

const formatDate = (d: string) =>
  new Date(d).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })

const fetchUsers = async () => {
  loading.value = true
  try {
    users.value = await userApi.getAllUsers()
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const openEditDialog = (row: UserInfo) => {
  editForm.id = row.id
  editForm.username = row.username
  editForm.email = row.email
  editForm.role = row.role
  editForm.is_active = row.is_active
  dialogVisible.value = true
}

const handleSave = async () => {
  saving.value = true
  try {
    const updated = await userApi.updateUser(editForm.id, {
      role: editForm.role,
      is_active: editForm.is_active
    })
    const idx = users.value.findIndex(u => u.id === updated.id)
    if (idx !== -1) users.value[idx] = updated
    dialogVisible.value = false
    ElMessage.success('用户信息已更新')
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

const toggleStatus = async (row: UserInfo) => {
  toggling.value = row.id
  try {
    const updated = await userApi.updateUser(row.id, { is_active: !row.is_active })
    const idx = users.value.findIndex(u => u.id === updated.id)
    if (idx !== -1) users.value[idx] = updated
    ElMessage.success(updated.is_active ? '用户已启用' : '用户已禁用')
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '操作失败')
  } finally {
    toggling.value = null
  }
}

const handleCreateUser = () => {
  createForm.username = ''
  createForm.email = ''
  createForm.password = ''
  createForm.role = 'user'
  createDialogVisible.value = true
}

const handleCreate = async () => {
  if (!createFormRef.value) return
  await createFormRef.value.validate(async (valid) => {
    if (!valid) return
    creating.value = true
    try {
      await userApi.createUser({
        username: createForm.username,
        email: createForm.email,
        password: createForm.password,
        role: createForm.role
      })
      ElMessage.success('用户创建成功')
      createDialogVisible.value = false
      await fetchUsers()
    } catch (err: any) {
      ElMessage.error(err?.response?.data?.detail || '创建用户失败')
    } finally {
      creating.value = false
    }
  })
}

onMounted(() => { fetchUsers() })
</script>

<style scoped>
.users-view {
  max-width: 1200px;
  margin: 0 auto;
}

.header-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
