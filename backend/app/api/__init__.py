"""API 模块"""
from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.tickets import router as tickets_router
from app.api.users import router as users_router
from app.api.audit import router as audit_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(tickets_router)
api_router.include_router(users_router)
api_router.include_router(audit_router)
