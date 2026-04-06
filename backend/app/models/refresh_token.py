"""Refresh Token 模型"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, BINARY
from sqlalchemy.dialects.mysql import BINARY as MySQL_BINARY
from sqlalchemy.orm import relationship
from app.models.base import Base


class RefreshToken(Base):
    """Refresh Token 表"""
    __tablename__ = "refresh_tokens"

    id = Column(MySQL_BINARY(16), primary_key=True, default=uuid.uuid4)
    user_id = Column(MySQL_BINARY(16), ForeignKey("users.id"), nullable=False, index=True)
    token_id = Column(String(36), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # 关系
    user = relationship("User", back_populates="refresh_tokens")

    def __repr__(self):
        return f"<RefreshToken {self.token_id[:8]}...>"
