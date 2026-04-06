import api from './client'
import type {
  Ticket,
  TicketDetail,
  TicketListResponse
} from '@/types'

// 工单请求类型
export interface CreateTicketRequest {
  title: string
  description: string
  priority?: 'low' | 'medium' | 'high'
}

export interface UpdateTicketRequest {
  title?: string
  description?: string
  priority?: 'low' | 'medium' | 'high'
}

export interface AssignTicketRequest {
  assignee_id?: string | null
}

export interface ChangeStatusRequest {
  status: 'pending' | 'in_progress' | 'resolved' | 'closed'
}

export interface TicketFilters {
  status?: string
  priority?: string
  assignee_id?: string
  page?: number
  limit?: number
}

// 工单 API
export const ticketApi = {
  // 获取工单列表
  getTickets: (filters?: TicketFilters): Promise<TicketListResponse> => {
    const params = new URLSearchParams()
    if (filters?.status) params.set('status', filters.status)
    if (filters?.priority) params.set('priority', filters.priority)
    if (filters?.assignee_id) params.set('assignee_id', filters.assignee_id)
    if (filters?.page) params.set('page', String(filters.page))
    if (filters?.limit) params.set('limit', String(filters.limit))
    const query = params.toString()
    return api.get(`/tickets${query ? `?${query}` : ''}`).then(res => res.data)
  },

  // 获取单个工单
  getTicket: (id: string): Promise<TicketDetail> =>
    api.get(`/tickets/${id}`).then(res => res.data),

  // 创建工单
  createTicket: (data: CreateTicketRequest): Promise<Ticket> =>
    api.post('/tickets', data).then(res => res.data),

  // 更新工单
  updateTicket: (id: string, data: UpdateTicketRequest): Promise<Ticket> =>
    api.put(`/tickets/${id}`, data).then(res => res.data),

  // 删除工单（软删除）
  deleteTicket: (id: string): Promise<void> =>
    api.delete(`/tickets/${id}`).then(res => res.data),

  // 指派工单
  assignTicket: (id: string, data: AssignTicketRequest): Promise<Ticket> =>
    api.post(`/tickets/${id}/assign`, data).then(res => res.data),

  // 变更状态
  changeStatus: (id: string, data: ChangeStatusRequest): Promise<Ticket> =>
    api.patch(`/tickets/${id}/status`, data).then(res => res.data),
}
