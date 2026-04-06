<template>
  <div class="create-ticket-view">
    <el-card class="form-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>创建工单</span>
        </div>
      </template>

      <el-form
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
            placeholder="请详细描述您的问题，包括：
1. 问题现象
2. 发生时间
3. 涉及的系统或设备
4. 联系方式"
          />
        </el-form-item>

        <el-form-item label="优先级" prop="priority">
          <el-radio-group v-model="form.priority">
            <el-radio value="low">低</el-radio>
            <el-radio value="medium">中</el-radio>
            <el-radio value="high">高</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="附件">
          <el-upload
            action="#"
            :auto-upload="false"
            :limit="5"
            accept=".jpg,.png,.pdf,.doc,.docx"
          >
            <el-button type="primary" plain>
              <el-icon><Upload /></el-icon>
              点击上传
            </el-button>
            <template #tip>
              <div class="upload-tip">支持 jpg、png、pdf、doc 格式，最多 5 个文件</div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            {{ submitting ? '提交中...' : '提交工单' }}
          </el-button>
          <el-button @click="router.push('/tickets')">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ticketApi } from '@/api/ticket'

const router = useRouter()
const formRef = ref<FormInstance>()
const submitting = ref(false)

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
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true

    try {
      await ticketApi.createTicket({
        title: form.title,
        description: form.description,
        priority: form.priority
      })

      ElMessage.success('工单创建成功！')
      router.push('/tickets')
    } catch (error: any) {
      ElMessage.error(error?.response?.data?.detail || '创建失败，请稍后重试')
    } finally {
      submitting.value = false
    }
  })
}
</script>

<style scoped>
.create-ticket-view {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
}

.ticket-form {
  max-width: 600px;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}
</style>
