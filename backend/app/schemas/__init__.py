"""Schemas 模块"""
from app.schemas.base import BaseSchema, TimestampSchema
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    LogoutRequest,
    TokenResponse,
    RegisterResponse,
    MessageResponse,
    UserBriefResponse,
    UserResponse,
)
from app.schemas.ticket import (
    CreateTicketRequest,
    UpdateTicketRequest,
    AssignTicketRequest,
    ChangeStatusRequest,
    TicketResponse,
    TicketDetailResponse,
    TicketListResponse,
    StatusHistoryItem,
    STATUS_TRANSITIONS,
)
from app.schemas.audit_log import (
    AuditLogResponse,
    AuditLogListResponse,
)

__all__ = [
    "BaseSchema",
    "TimestampSchema",
    "RegisterRequest",
    "LoginRequest",
    "LogoutRequest",
    "TokenResponse",
    "RegisterResponse",
    "MessageResponse",
    "UserBriefResponse",
    "UserResponse",
    "CreateTicketRequest",
    "UpdateTicketRequest",
    "AssignTicketRequest",
    "ChangeStatusRequest",
    "TicketResponse",
    "TicketDetailResponse",
    "TicketListResponse",
    "StatusHistoryItem",
    "STATUS_TRANSITIONS",
    "AuditLogResponse",
    "AuditLogListResponse",
]
