"""审计日志服务"""
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, Dict, Any, List
from app.models import AuditLog
from app.schemas.audit_log import AuditLogListResponse, AuditLogResponse


class AuditService:
    """审计日志服务"""

    @staticmethod
    async def log(
        db: AsyncSession,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """记录审计日志"""
        # 转换字符串 ID 为二进制
        resource_id_bin = None
        if resource_id:
            resource_id_bin = uuid.UUID(resource_id).bytes

        log_entry = AuditLog(
            id=uuid.uuid4().bytes,
            user_id=uuid.UUID(user_id).bytes,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id_bin,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent[:500] if user_agent else None
        )
        db.add(log_entry)
        await db.commit()
        await db.refresh(log_entry)
        return log_entry

    @staticmethod
    def _bytes_to_hex(data: bytes) -> str:
        """字节转十六进制字符串"""
        return bytes(data).hex() if data else None

    @staticmethod
    async def get_logs(
        db: AsyncSession,
        action: Optional[str] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> AuditLogListResponse:
        """获取审计日志列表"""
        query = select(AuditLog)
        count_query = select(func.count(AuditLog.id))

        if action:
            query = query.where(AuditLog.action == action)
            count_query = count_query.where(AuditLog.action == action)
        if user_id:
            user_id_bin = uuid.UUID(user_id).bytes
            query = query.where(AuditLog.user_id == user_id_bin)
            count_query = count_query.where(AuditLog.user_id == user_id_bin)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
            count_query = count_query.where(AuditLog.resource_type == resource_type)
        if resource_id:
            resource_id_bin = uuid.UUID(resource_id).bytes
            query = query.where(AuditLog.resource_id == resource_id_bin)
            count_query = count_query.where(AuditLog.resource_id == resource_id_bin)

        # 总数
        total = (await db.execute(count_query)).scalar()

        # 分页
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit).order_by(AuditLog.created_at.desc())
        result = await db.execute(query)
        logs = result.scalars().all()

        items = []
        for log in logs:
            items.append(AuditLogResponse(
                id=AuditService._bytes_to_hex(log.id),
                user_id=AuditService._bytes_to_hex(log.user_id),
                action=log.action,
                resource_type=log.resource_type,
                resource_id=AuditService._bytes_to_hex(log.resource_id) if log.resource_id else None,
                old_value=log.old_value,
                new_value=log.new_value,
                ip_address=log.ip_address,
                user_agent=log.user_agent,
                created_at=log.created_at
            ))

        return AuditLogListResponse(items=items, total=total, page=page, limit=limit)
