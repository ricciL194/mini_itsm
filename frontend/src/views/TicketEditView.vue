<template>
  <div class="edit-ticket-view">
    <el-card class="form-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>编辑工单</span>
          <el-button text @click="router.push(`/tickets/${ticketId}`)">
            ← 返回详情
          </el-button>
        </div>
      </template>

      <el-skeleton v-if="loading" :rows="6" animated />
      <el-form
        v-else
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        class="ticket-form"
      >
        <el-form-item label="工单标题" prop="title">
          <el-input
            v-model="form.title"
            placeholder="请简要描述您的问题"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="工单描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="6"
            placeholder="请详细描述您的问题"
          />
        </el-form-item>

        <el-form-item label="优先级" prop="priority">
          <el-radio-group v-model="form.priority">
            <el-radio value="low">低</el-radio>
            <el-radio value="medium">中</el-radio>
            <el-radio value="high">高</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            保存修改
          </el-button>
          <el-button @click="router.push(`/tickets/${ticketId}`)">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ticketApi } from '@/api/ticket'
import type { FormInstance, FormRules } from 'element-plus'

const route = useRoute()
const router = useRouter()
const formRef = ref<FormInstance>()
const submitting = ref(false)
const loading = ref(false)

const ticketId = route.params.id as string

const form = reactive({
  title: '',
  description: '',
  priority: 'medium' as 'low' | 'medium' | 'high'
})

const rules: FormRules = {
  title: [
    { required: true, message: '请输入工单标题', trigger: 'blur' },
    { min: 5, max: 200, message: '标题长度 5-200 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入工单描述', trigger: 'blur' },
    { min: 10, message: '描述至少 10 个字符', trigger: 'blur' }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      await ticketApi.updateTicket(ticketId, {
        title: form.title,
        description: form.description,
        priority: form.priority
      })
      ElMessage.success('修改已保存')
      router.push(`/tickets/${ticketId}`)
    } catch (err: any) {
      ElMessage.error(err?.response?.data?.detail || '保存失败，请稍后重试')
    } finally {
      submitting.value = false
    }
  })
}

onMounted(async () => {
  loading.value = true
  try {
    const ticket = await ticketApi.getTicket(ticketId)
    form.title = ticket.title
    form.description = ticket.description
    form.priority = ticket.priority as 'low' | 'medium' | 'high'
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '加载工单失败')
    router.push('/tickets')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.edit-ticket-view {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ticket-form {
  max-width: 600px;
}
</style>
