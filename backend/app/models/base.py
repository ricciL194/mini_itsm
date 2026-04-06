"""基础模型"""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def generate_uuid() -> uuid.UUID:
    return uuid.uuid4()


class TimestampMixin:
    """时间戳混入"""
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
