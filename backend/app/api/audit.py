"""审计日志路由"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import User
from app.schemas import AuditLogListResponse
from app.api.deps import get_current_user, get_current_admin_user
from app.services import AuditService

router = APIRouter(prefix="/audit", tags=["审计日志"])


@router.get("", response_model=AuditLogListResponse)
async def list_audit_logs(
    action: Optional[str] = Query(None, description="操作类型过滤"),
    resource_type: Optional[str] = Query(None, description="资源类型过滤"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """获取审计日志列表（仅管理员）"""
    return await AuditService.get_logs(
        db=db,
        action=action,
        resource_type=resource_type,
        page=page,
        limit=limit
    )


@router.get("/ticket/{ticket_id}", response_model=AuditLogListResponse)
async def get_ticket_audit_logs(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取指定工单的审计日志"""
    return await AuditService.get_logs(
        db=db,
        resource_type="ticket",
        resource_id=ticket_id,
        page=1,
        limit=100
    )
