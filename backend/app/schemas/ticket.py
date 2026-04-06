"""工单相关 Schema"""
from datetime import datetime
from typing import Optional, List
from pydantic import Field
from app.schemas.base import BaseSchema
from app.schemas.auth import UserBriefResponse


# ============ Enums ============

class TicketPriority(str):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TicketStatus(str):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


# ============ Request ============

class CreateTicketRequest(BaseSchema):
    """创建工单请求"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")


class UpdateTicketRequest(BaseSchema):
    """更新工单请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")


class AssignTicketRequest(BaseSchema):
    """指派工单请求"""
    assignee_id: Optional[str] = Field(None)


class ChangeStatusRequest(BaseSchema):
    """变更状态请求"""
    status: str = Field(..., pattern="^(pending|in_progress|resolved|closed)$")


# ============ Response ============

class StatusHistoryItem(BaseSchema):
    """状态历史条目"""
    id: str
    from_status: Optional[str]
    to_status: str
    changed_by: UserBriefResponse
    created_at: datetime


class TicketResponse(BaseSchema):
    """工单响应"""
    id: str
    title: str
    description: str
    priority: str
    status: str
    creator: UserBriefResponse
    assignee: Optional[UserBriefResponse]
    created_at: datetime
    updated_at: datetime


class TicketDetailResponse(TicketResponse):
    """工单详情响应"""
    status_history: List[StatusHistoryItem] = []


class TicketListResponse(BaseSchema):
    """工单列表响应"""
    items: List[TicketResponse]
    total: int
    page: int
    limit: int


# ============ Status Workflow ============

# 允许的状态转换映射
STATUS_TRANSITIONS = {
    "pending": ["in_progress", "closed"],
    "in_progress": ["resolved", "pending"],
    "resolved": ["closed", "in_progress"],
    "closed": [],
}
