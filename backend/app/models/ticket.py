"""工单模型"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Enum as SQLEnum, ForeignKey, DateTime, BINARY
from sqlalchemy.dialects.mysql import BINARY as MySQL_BINARY
from sqlalchemy.orm import relationship
import enum
from app.models.base import Base, TimestampMixin


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TicketStatus(str, enum.Enum):
    PENDING = "pending"           # 待处理
    IN_PROGRESS = "in_progress"   # 处理中
    RESOLVED = "resolved"         # 已解决
    CLOSED = "closed"            # 已关闭


class Ticket(Base, TimestampMixin):
    """工单表"""
    __tablename__ = "tickets"

    id = Column(MySQL_BINARY(16), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(SQLEnum(TicketPriority), default=TicketPriority.MEDIUM, nullable=False)
    status = Column(SQLEnum(TicketStatus), default=TicketStatus.PENDING, nullable=False, index=True)
    category = Column(String(50), nullable=True)
    closed_at = Column(DateTime, nullable=True)
    closed_reason = Column(String(200), nullable=True)

    # 外键
    creator_id = Column(MySQL_BINARY(16), ForeignKey("users.id"), nullable=False, index=True)
    assignee_id = Column(MySQL_BINARY(16), ForeignKey("users.id"), nullable=True, index=True)

    # 软删除
    deleted_at = Column(DateTime, nullable=True)

    # 关系
    creator = relationship("User", back_populates="tickets", foreign_keys=[creator_id])
    assignee = relationship("User", back_populates="assigned_tickets", foreign_keys=[assignee_id])
    status_history = relationship("TicketStatusHistory", back_populates="ticket", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Ticket {self.title[:30]}>"

    @property
    def id_str(self) -> str:
        return bytes(self.id).hex() if self.id else None


class TicketStatusHistory(Base, TimestampMixin):
    """工单状态变更历史表"""
    __tablename__ = "ticket_status_history"

    id = Column(MySQL_BINARY(16), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(MySQL_BINARY(16), ForeignKey("tickets.id"), nullable=False, index=True)
    from_status = Column(SQLEnum(TicketStatus), nullable=True)
    to_status = Column(SQLEnum(TicketStatus), nullable=False)
    changed_by_id = Column(MySQL_BINARY(16), ForeignKey("users.id"), nullable=False)
    change_reason = Column(String(200), nullable=True)

    # 关系
    ticket = relationship("Ticket", back_populates="status_history")
    changed_by = relationship("User")

    def __repr__(self):
        return f"<TicketStatusHistory {self.from_status} -> {self.to_status}>"
