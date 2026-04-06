"""审计日志模型"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Index, JSON
from sqlalchemy.dialects.mysql import BINARY as MySQL_BINARY
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class AuditLog(Base, TimestampMixin):
    """审计日志表"""
    __tablename__ = "audit_logs"

    id = Column(MySQL_BINARY(16), primary_key=True, default=uuid.uuid4)
    user_id = Column(MySQL_BINARY(16), ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(MySQL_BINARY(16), nullable=True, index=True)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # 关系
    user = relationship("User", back_populates="audit_logs")
    # 注意：ticket 关系通过 resource_id 和 resource_type='ticket' 实现，非外键关联

    # 索引
    __table_args__ = (
        Index("idx_audit_resource", "resource_type", "resource_id"),
        Index("idx_audit_created", "created_at"),
    )

    def __repr__(self):
        return f"<AuditLog {self.action} by user>"
