"""用户模型"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, DateTime
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.orm import relationship
import enum
from app.models.base import Base, TimestampMixin


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base, TimestampMixin):
    """用户表"""
    __tablename__ = "users"

    id = Column(BINARY(16), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # 关系
    tickets = relationship("Ticket", back_populates="creator", foreign_keys="Ticket.creator_id")
    assigned_tickets = relationship("Ticket", back_populates="assignee", foreign_keys="Ticket.assignee_id")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self):
        return f"<User {self.username}>"

    @property
    def id_str(self) -> str:
        return bytes(self.id).hex() if self.id else None
