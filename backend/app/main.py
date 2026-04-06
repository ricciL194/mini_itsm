"""FastAPI 应用入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api import api_router


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="迷你工单管理系统 API",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
async def startup():
    """启动时初始化"""
    await init_db()


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": settings.APP_VERSION}
