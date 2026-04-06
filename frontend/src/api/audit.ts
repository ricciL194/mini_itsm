import api from './client'

export interface AuditLog {
  id: string
  user_id: string
  action: string
  resource_type: string
  resource_id: string | null
  old_value: Record<string, any> | null
  new_value: Record<string, any> | null
  ip_address: string | null
  user_agent: string | null
  created_at: string
}

export interface AuditLogListResponse {
  items: AuditLog[]
  total: number
  page: number
  limit: number
}

export interface AuditFilters {
  action?: string
  resource_type?: string
  page?: number
  limit?: number
}

export const auditApi = {
  getLogs: (filters?: AuditFilters): Promise<AuditLogListResponse> => {
    const params = new URLSearchParams()
    if (filters?.action) params.set('action', filters.action)
    if (filters?.resource_type) params.set('resource_type', filters.resource_type)
    if (filters?.page) params.set('page', String(filters.page))
    if (filters?.limit) params.set('limit', String(filters.limit))
    const query = params.toString()
    return api.get(`/audit${query ? `?${query}` : ''}`).then(res => res.data)
  },
}
