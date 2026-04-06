"""认证相关 Schema"""
from datetime import datetime
from pydantic import EmailStr, Field, field_validator
from app.schemas.base import BaseSchema


# ============ Request ============

class RegisterRequest(BaseSchema):
    """注册请求"""
    username: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("username")
    def validate_username(cls, v: str) -> str:
        # 允许字母、数字、下划线、中文
        if not v.replace("_", "").replace("-", "").isalnum() and not any('\u4e00' <= c <= '\u9fff' for c in v):
            raise ValueError("用户名只能包含字母、数字、下划线和中文")
        return v


class LoginRequest(BaseSchema):
    """登录请求"""
    email: EmailStr
    password: str


class LogoutRequest(BaseSchema):
    """登出请求"""
    refresh_token: str | None = None


# ============ Response ============

class TokenResponse(BaseSchema):
    """Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RegisterResponse(BaseSchema):
    """注册响应"""
    id: str
    username: str
    email: str
    message: str = "注册成功"


class MessageResponse(BaseSchema):
    """通用消息响应"""
    message: str


class UserBriefResponse(BaseSchema):
    """用户简要信息"""
    id: str
    username: str


class UserResponse(BaseSchema):
    """用户响应"""
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
