"""基础 Schema"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """基础 Schema 配置"""
    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(BaseModel):
    """时间戳 Schema"""
    created_at: datetime
    updated_at: datetime
