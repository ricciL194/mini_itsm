"""审计日志 Schema"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.schemas.base import BaseSchema


class AuditLogResponse(BaseSchema):
    """审计日志响应"""
    id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: Optional[str]
    old_value: Optional[dict]
    new_value: Optional[dict]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime


class AuditLogListResponse(BaseModel):
    """审计日志列表响应"""
    items: List[AuditLogResponse]
    total: int
    page: int
    limit: int
