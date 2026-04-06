// 用户类型
export interface User {
  id: string
  username: string
  email: string
  role: 'user' | 'admin'
  is_active: boolean
  created_at: string
}

// 认证相关类型
export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface RegisterResponse {
  id: string
  username: string
  email: string
  message: string
}

// 工单相关类型
export interface Ticket {
  id: string
  title: string
  description: string
  priority: 'low' | 'medium' | 'high'
  status: 'pending' | 'in_progress' | 'resolved' | 'closed'
  creator: {
    id: string
    username: string
  }
  assignee: {
    id: string
    username: string
  } | null
  created_at: string
  updated_at: string
}

export interface TicketListResponse {
  items: Ticket[]
  total: number
  page: number
  limit: number
}

export interface StatusHistoryItem {
  id: string
  from_status: string | null
  to_status: string
  changed_by: { id: string; username: string }
  created_at: string
}

export interface TicketDetail extends Ticket {
  status_history: StatusHistoryItem[]
}

// 审计日志
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
