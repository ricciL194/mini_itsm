# 后端模块详细设计

## 1. 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   │
│   ├── api/                    # API 路由层
│   │   ├── __init__.py
│   │   ├── deps.py             # 路由依赖（get_db, get_current_user）
│   │   ├── auth.py             # 认证相关路由
│   │   ├── users.py            # 用户管理路由
│   │   ├── tickets.py          # 工单管理路由
│   │   └── audit_logs.py       # 审计日志路由
│   │
│   ├── core/                   # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py           # 应用配置（环境变量）
│   │   ├── database.py         # 数据库连接
│   │   ├── security.py         # JWT + 密码工具
│   │   └── exceptions.py       # 自定义异常
│   │
│   ├── models/                 # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── base.py             # 基础模型类
│   │   ├── user.py             # User 模型
│   │   ├── refresh_token.py    # RefreshToken 模型
│   │   ├── ticket.py           # Ticket 模型
│   │   ├── ticket_status.py    # TicketStatusHistory 模型
│   │   └── audit_log.py        # AuditLog 模型
│   │
│   ├── schemas/                # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── base.py             # 基础 schema
│   │   ├── auth.py             # 认证相关 schema
│   │   ├── user.py             # 用户相关 schema
│   │   ├── ticket.py           # 工单相关 schema
│   │   └── audit_log.py        # 审计日志 schema
│   │
│   ├── services/               # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py     # 认证业务逻辑
│   │   ├── user_service.py     # 用户业务逻辑
│   │   ├── ticket_service.py   # 工单业务逻辑
│   │   └── audit_service.py    # 审计日志业务逻辑
│   │
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       └── pagination.py        # 分页工具
│
├── alembic/                    # 数据库迁移
│   ├── env.py
│   └── versions/
│
├── tests/                      # 测试
│   ├── __init__.py
│   ├── conftest.py
│   ├── api/
│   ├── services/
│   └── factories/
│
├── .env.example                # 环境变量示例
├── alembic.ini
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml
```

## 2. 核心配置文件

### 2.1 app/core/config.py

```python
"""应用配置"""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    APP_NAME: str = "Mini ITSM"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 数据库
    DATABASE_URL: str = "mysql+pymysql://user:password@localhost:3306/mini_itsm"

    # JWT 配置
    JWT_SECRET_KEY: str  # 必须设置，使用 openssl rand -hex 32 生成
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 密码配置
    PASSWORD_MIN_LENGTH: int = 8

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

### 2.2 app/core/database.py

```python
"""数据库配置"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings

settings = get_settings()

# 异步引擎（推荐，用于 FastAPI）
DATABASE_URL = settings.DATABASE_URL.replace(
    "mysql+pymysql://", "mysql+aiomysql://"
)

async_engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """初始化数据库（创建所有表）"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

### 2.3 app/core/security.py

```python
"""安全工具：JWT + 密码哈希"""
from datetime import datetime, timedelta, timezone
from typing import Any
import uuid

from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import get_settings

settings = get_settings()

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)


def create_access_token(
    user_id: str,
    role: str,
    expires_delta: timedelta | None = None
) -> str:
    """创建 Access Token"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode: dict[str, Any] = {
        "sub": user_id,
        "type": "access",
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> tuple[str, str]:
    """创建 Refresh Token，返回 (token, token_id)"""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    token_id = str(uuid.uuid4())

    to_encode: dict[str, Any] = {
        "sub": user_id,
        "type": "refresh",
        "jti": token_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, token_id


def decode_token(token: str) -> dict[str, Any] | None:
    """解码 Token"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_access_token(token: str) -> dict[str, Any] | None:
    """验证 Access Token"""
    payload = decode_token(token)
    if payload and payload.get("type") == "access":
        return payload
    return None


def verify_refresh_token(token: str) -> dict[str, Any] | None:
    """验证 Refresh Token"""
    payload = decode_token(token)
    if payload and payload.get("type") == "refresh":
        return payload
    return None
```

## 3. 数据库模型

### 3.1 app/models/base.py

```python
"""基础模型"""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.mysql import BINARY
from app.core.database import Base


class BaseModel(Base):
    """带通用字段的基础模型"""
    __abstract__ = True

    id = Column(BINARY(16), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    @staticmethod
    def uuid_to_str(obj: "BaseModel") -> "BaseModel":
        """将 UUID 从二进制转换为字符串"""
        if obj.id:
            obj.id = str(obj.id)
        return obj
```

### 3.2 app/models/user.py

```python
"""用户模型"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base, BaseModel):
    """用户表"""
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # 软删除
    deleted_at = Column(DateTime, nullable=True)

    # 关系
    tickets = relationship("Ticket", back_populates="creator", foreign_keys="Ticket.creator_id")
    assigned_tickets = relationship("Ticket", back_populates="assignee", foreign_keys="Ticket.assignee_id")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self):
        return f"<User {self.username}>"
```

### 3.3 app/models/ticket.py

```python
"""工单模型"""
from sqlalchemy import Column, String, Text, Enum, ForeignKey
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
from app.models.base import BaseModel


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TicketStatus(str, enum.Enum):
    PENDING = "pending"          # 待处理
    IN_PROGRESS = "in_progress"  # 处理中
    RESOLVED = "resolved"        # 已解决
    CLOSED = "closed"            # 已关闭


class Ticket(Base, BaseModel):
    """工单表"""
    __tablename__ = "tickets"

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.PENDING, nullable=False, index=True)

    # 外键
    creator_id = Column(BINARY(16), ForeignKey("users.id"), nullable=False, index=True)
    assignee_id = Column(BINARY(16), ForeignKey("users.id"), nullable=True, index=True)

    # 软删除
    deleted_at = Column(Column.DateTime, nullable=True)

    # 关系
    creator = relationship("User", back_populates="tickets", foreign_keys=[creator_id])
    assignee = relationship("User", back_populates="assigned_tickets", foreign_keys=[assignee_id])
    status_history = relationship("TicketStatusHistory", back_populates="ticket", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="ticket")

    def __repr__(self):
        return f"<Ticket {self.id}: {self.title}>"
```

### 3.4 app/models/ticket_status_history.py

```python
"""工单状态历史"""
from sqlalchemy import Column, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import BaseModel


class TicketStatusHistory(Base, BaseModel):
    """工单状态变更历史表"""
    __tablename__ = "ticket_status_history"

    ticket_id = Column(BINARY(16), ForeignKey("tickets.id"), nullable=False, index=True)
    from_status = Column(Enum(TicketStatus), nullable=True)  # None 表示初始创建
    to_status = Column(Enum(TicketStatus), nullable=False)
    changed_by_id = Column(BINARY(16), ForeignKey("users.id"), nullable=False)

    # 关系
    ticket = relationship("Ticket", back_populates="status_history")
    changed_by = relationship("User")

    def __repr__(self):
        return f"<TicketStatusHistory {self.from_status} -> {self.to_status}>"
```

### 3.5 app/models/audit_log.py

```python
"""审计日志模型"""
from sqlalchemy import Column, String, Text, ForeignKey, Index
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import BaseModel


class AuditLog(Base, BaseModel):
    """审计日志表"""
    __tablename__ = "audit_logs"

    user_id = Column(BINARY(16), ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)  # 如 ticket.create
    resource_type = Column(String(50), nullable=False)  # 如 ticket, user
    resource_id = Column(BINARY(16), nullable=True, index=True)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 支持
    user_agent = Column(String(500), nullable=True)

    # 关系
    user = relationship("User", back_populates="audit_logs")
    ticket = relationship("Ticket", back_populates="audit_logs")

    # 索引
    __table_args__ = (
        Index("idx_audit_resource", "resource_type", "resource_id"),
        Index("idx_audit_created", "created_at"),
    )

    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_id}>"
```

## 4. Pydantic Schemas

### 4.1 app/schemas/base.py

```python
"""基础 Schema"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict
import uuid


class BaseSchema(BaseModel):
    """基础 Schema 配置"""
    model_config = ConfigDict(from_attributes=True)


class UUIDSchema(BaseSchema):
    """带 UUID 的 Schema"""
    id: uuid.UUID


class TimestampSchema(BaseSchema):
    """带时间戳的 Schema"""
    created_at: datetime
    updated_at: datetime
```

### 4.2 app/schemas/auth.py

```python
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
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v.replace("_", "").replace("-", "").isalnum() and not any('\u4e00' <= c <= '\u9fff' for c in v):
            raise ValueError("用户名只能包含字母、数字、下划线和中文")
        return v


class LoginRequest(BaseSchema):
    """登录请求"""
    email: EmailStr
    password: str


class RefreshRequest(BaseSchema):
    """刷新 Token 请求（使用 Bearer Token）"""


class LogoutRequest(BaseSchema):
    """登出请求"""
    refresh_token: str


# ============ Response ============

class TokenResponse(BaseSchema):
    """Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Access Token 过期时间（秒）


class RegisterResponse(BaseSchema):
    """注册响应"""
    id: str
    username: str
    email: str
    message: str = "注册成功"


class MessageResponse(BaseSchema):
    """通用消息响应"""
    message: str
```

### 4.3 app/schemas/user.py

```python
"""用户相关 Schema"""
from datetime import datetime
from pydantic import EmailStr, Field
from app.schemas.base import BaseSchema


class UserResponse(BaseSchema):
    """用户响应"""
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime


class UserListResponse(BaseSchema):
    """用户列表响应"""
    items: list[UserResponse]
    total: int
    page: int
    limit: int


class UpdateUserRoleRequest(BaseSchema):
    """更新用户角色请求"""
    role: str = Field(..., pattern="^(user|admin)$")


class DeactivateUserRequest(BaseSchema):
    """禁用用户请求"""
    pass  # 只需用户 ID
```

### 4.4 app/schemas/ticket.py

```python
"""工单相关 Schema"""
from datetime import datetime
from pydantic import Field, field_validator
from typing import Optional
from app.schemas.base import BaseSchema


# ============ Enums ============

class TicketPriority(str):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TicketStatus(str):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


# ============ Request ============

class CreateTicketRequest(BaseSchema):
    """创建工单请求"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    priority: TicketPriority = TicketPriority.MEDIUM


class UpdateTicketRequest(BaseSchema):
    """更新工单请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    priority: Optional[TicketPriority] = None


class AssignTicketRequest(BaseSchema):
    """指派工单请求"""
    assignee_id: str | None = Field(None, description="为空表示取消指派")


class ChangeStatusRequest(BaseSchema):
    """变更状态请求"""
    status: TicketStatus


class TicketFilter(BaseSchema):
    """工单筛选"""
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assignee_id: Optional[str] = None
    creator_id: Optional[str] = None


# ============ Response ============

class UserBrief(BaseSchema):
    """用户简要信息"""
    id: str
    username: str


class StatusHistoryItem(BaseSchema):
    """状态历史条目"""
    id: str
    from_status: str | None
    to_status: str
    changed_by: UserBrief
    created_at: datetime


class TicketResponse(BaseSchema):
    """工单响应"""
    id: str
    title: str
    description: str
    priority: str
    status: str
    creator: UserBrief
    assignee: UserBrief | None
    created_at: datetime
    updated_at: datetime


class TicketDetailResponse(TicketResponse):
    """工单详情响应"""
    status_history: list[StatusHistoryItem]


class TicketListResponse(BaseSchema):
    """工单列表响应"""
    items: list[TicketResponse]
    total: int
    page: int
    limit: int


# ============ Status Workflow ============

# 允许的状态转换映射
STATUS_TRANSITIONS = {
    "pending": ["in_progress", "closed"],
    "in_progress": ["resolved", "pending"],
    "resolved": ["closed", "in_progress"],
    "closed": [],  # 终态
}
```

## 5. API 路由设计

### 5.1 app/api/deps.py

```python
"""API 依赖"""
from typing import Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import verify_access_token, verify_refresh_token
from app.models.user import User, UserRole

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """获取当前用户"""
    token = credentials.credentials
    payload = verify_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或已过期的 Token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )
    return current_user


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """获取当前管理员用户"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


def get_client_ip(request: Request) -> str:
    """获取客户端 IP"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
```

### 5.2 app/api/auth.py

```python
"""认证路由"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token
)
from app.core.config import get_settings
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    TokenResponse,
    LogoutRequest,
    MessageResponse
)
from app.api.deps import get_current_user, get_client_ip

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    # 检查邮箱是否已存在
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )

    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户名已被使用"
        )

    # 创建用户
    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return RegisterResponse(
        id=str(user.id),
        username=user.username,
        email=user.email
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    # 查找用户
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    # 验证密码（统一错误提示，防止用户名枚举）
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )

    # 检查账户状态
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )

    # 生成 Token
    access_token = create_access_token(str(user.id), user.role.value)
    refresh_token, token_id = create_refresh_token(str(user.id))

    # 存储 Refresh Token
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token_id=token_id,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("user-agent", "")[:500]
    )
    db.add(db_refresh_token)
    await db.commit()

    settings = get_settings()
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """刷新 Token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少 Refresh Token"
        )

    token = auth_header.split(" ")[1]
    payload = verify_refresh_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 Refresh Token"
        )

    # 查找 Token 记录
    token_id = payload.get("jti")
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_id == token_id,
            RefreshToken.revoked == False
        )
    )
    db_token = result.scalar_one_or_none()

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh Token 已失效"
        )

    # 撤销旧 Token
    db_token.revoked = True

    # 查找用户
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )

    # 生成新 Token
    new_access_token = create_access_token(str(user.id), user.role.value)
    new_refresh_token, new_token_id = create_refresh_token(str(user.id))

    # 存储新 Refresh Token
    new_db_token = RefreshToken(
        user_id=user.id,
        token_id=new_token_id,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("user-agent", "")[:500]
    )
    db.add(new_db_token)
    await db.commit()

    settings = get_settings()
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    data: LogoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """用户登出"""
    payload = verify_refresh_token(data.refresh_token)
    if payload:
        token_id = payload.get("jti")
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token_id == token_id,
                RefreshToken.user_id == current_user.id
            )
        )
        db_token = result.scalar_one_or_none()
        if db_token:
            db_token.revoked = True
            await db.commit()

    return MessageResponse(message="登出成功")


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }
```

### 5.3 app/api/tickets.py

```python
"""工单路由"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.user import User
from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.models.ticket_status_history import TicketStatusHistory
from app.schemas.ticket import (
    CreateTicketRequest,
    UpdateTicketRequest,
    AssignTicketRequest,
    ChangeStatusRequest,
    TicketResponse,
    TicketDetailResponse,
    TicketListResponse,
    UserBrief,
    StatusHistoryItem,
    STATUS_TRANSITIONS
)
from app.api.deps import get_current_user
from app.services.audit_service import AuditService

router = APIRouter(prefix="/tickets", tags=["工单"])


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    data: CreateTicketRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    audit_service: AuditService = Depends()
):
    """创建工单"""
    ticket = Ticket(
        title=data.title,
        description=data.description,
        priority=TicketPriority(data.priority),
        status=TicketStatus.PENDING,
        creator_id=current_user.id
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)

    # 记录初始状态
    history = TicketStatusHistory(
        ticket_id=ticket.id,
        from_status=None,
        to_status=TicketStatus.PENDING,
        changed_by_id=current_user.id
    )
    db.add(history)
    await db.commit()

    # 审计日志
    await audit_service.log(
        db=db,
        user_id=str(current_user.id),
        action="ticket.create",
        resource_type="ticket",
        resource_id=str(ticket.id),
        new_value={"title": ticket.title, "status": ticket.status.value}
    )

    return TicketResponse(
        id=str(ticket.id),
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority.value,
        status=ticket.status.value,
        creator=UserBrief(id=str(current_user.id), username=current_user.username),
        assignee=None,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at
    )


@router.get("", response_model=TicketListResponse)
async def list_tickets(
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = None,
    assignee_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取工单列表"""
    # 构建查询
    query = select(Ticket).where(Ticket.deleted_at.is_(None))
    count_query = select(func.count(Ticket.id)).where(Ticket.deleted_at.is_(None))

    # 非管理员只能看自己创建的和自己被指派的
    if current_user.role.value != "admin":
        query = query.where(
            (Ticket.creator_id == current_user.id) |
            (Ticket.assignee_id == current_user.id)
        )
        count_query = count_query.where(
            (Ticket.creator_id == current_user.id) |
            (Ticket.assignee_id == current_user.id)
        )

    # 筛选
    if status_filter:
        query = query.where(Ticket.status == TicketStatus(status_filter))
        count_query = count_query.where(Ticket.status == TicketStatus(status_filter))
    if priority:
        query = query.where(Ticket.priority == TicketPriority(priority))
        count_query = count_query.where(Ticket.priority == TicketPriority(priority))
    if assignee_id:
        query = query.where(Ticket.assignee_id == assignee_id)
        count_query = count_query.where(Ticket.assignee_id == assignee_id)

    # 总数
    total = (await db.execute(count_query)).scalar()

    # 分页
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Ticket.created_at.desc())
    result = await db.execute(query)
    tickets = result.scalars().all()

    # 构建响应
    items = []
    for ticket in tickets:
        creator_result = await db.execute(select(User).where(User.id == ticket.creator_id))
        creator = creator_result.scalar_one()
        assignee = None
        if ticket.assignee_id:
            assignee_result = await db.execute(select(User).where(User.id == ticket.assignee_id))
            assignee_user = assignee_result.scalar_one_or_none()
            if assignee_user:
                assignee = UserBrief(id=str(assignee_user.id), username=assignee_user.username)

        items.append(TicketResponse(
            id=str(ticket.id),
            title=ticket.title,
            description=ticket.description,
            priority=ticket.priority.value,
            status=ticket.status.value,
            creator=UserBrief(id=str(creator.id), username=creator.username),
            assignee=assignee,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at
        ))

    return TicketListResponse(items=items, total=total, page=page, limit=limit)


@router.get("/{ticket_id}", response_model=TicketDetailResponse)
async def get_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取工单详情"""
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()

    if not ticket or ticket.deleted_at:
        raise HTTPException(status_code=404, detail="工单不存在")

    # 权限检查
    if current_user.role.value != "admin" and \
       ticket.creator_id != current_user.id and \
       ticket.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此工单")

    # 获取创建者
    creator_result = await db.execute(select(User).where(User.id == ticket.creator_id))
    creator = creator_result.scalar_one()

    # 获取指派人
    assignee = None
    if ticket.assignee_id:
        assignee_result = await db.execute(select(User).where(User.id == ticket.assignee_id))
        assignee_user = assignee_result.scalar_one_or_none()
        if assignee_user:
            assignee = UserBrief(id=str(assignee_user.id), username=assignee_user.username)

    # 获取状态历史
    history_result = await db.execute(
        select(TicketStatusHistory)
        .where(TicketStatusHistory.ticket_id == ticket.id)
        .order_by(TicketStatusHistory.created_at)
    )
    history_items = []
    for history in history_result.scalars():
        changed_by_result = await db.execute(select(User).where(User.id == history.changed_by_id))
        changed_by = changed_by_result.scalar_one()
        history_items.append(StatusHistoryItem(
            id=str(history.id),
            from_status=history.from_status.value if history.from_status else None,
            to_status=history.to_status.value,
            changed_by=UserBrief(id=str(changed_by.id), username=changed_by.username),
            created_at=history.created_at
        ))

    return TicketDetailResponse(
        id=str(ticket.id),
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority.value,
        status=ticket.status.value,
        creator=UserBrief(id=str(creator.id), username=creator.username),
        assignee=assignee,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        status_history=history_items
    )


@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: str,
    data: UpdateTicketRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    audit_service: AuditService = Depends()
):
    """更新工单"""
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()

    if not ticket or ticket.deleted_at:
        raise HTTPException(status_code=404, detail="工单不存在")

    # 权限检查：创建者或指派人或管理员
    if current_user.role.value != "admin" and \
       ticket.creator_id != current_user.id and \
       ticket.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改此工单")

    # 更新字段
    old_value = {"title": ticket.title, "description": ticket.description, "priority": ticket.priority.value}
    if data.title is not None:
        ticket.title = data.title
    if data.description is not None:
        ticket.description = data.description
    if data.priority is not None:
        ticket.priority = TicketPriority(data.priority)

    await db.commit()
    await db.refresh(ticket)

    # 审计日志
    new_value = {"title": ticket.title, "description": ticket.description, "priority": ticket.priority.value}
    await audit_service.log(
        db=db,
        user_id=str(current_user.id),
        action="ticket.update",
        resource_type="ticket",
        resource_id=str(ticket.id),
        old_value=old_value,
        new_value=new_value
    )

    # 构建响应（省略，参考上面）
    ...


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    audit_service: AuditService = Depends()
):
    """删除工单（软删除）"""
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()

    if not ticket or ticket.deleted_at:
        raise HTTPException(status_code=404, detail="工单不存在")

    # 只有创建者和管理员可以删除
    if current_user.role.value != "admin" and ticket.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除此工单")

    # 软删除
    from datetime import datetime
    ticket.deleted_at = datetime.now()
    await db.commit()

    # 审计日志
    await audit_service.log(
        db=db,
        user_id=str(current_user.id),
        action="ticket.delete",
        resource_type="ticket",
        resource_id=str(ticket.id)
    )


@router.post("/{ticket_id}/assign", response_model=TicketResponse)
async def assign_ticket(
    ticket_id: str,
    data: AssignTicketRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    audit_service: AuditService = Depends()
):
    """指派工单"""
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()

    if not ticket or ticket.deleted_at:
        raise HTTPException(status_code=404, detail="工单不存在")

    # 权限检查：创建者或管理员
    if current_user.role.value != "admin" and ticket.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权指派此工单")

    # 验证指派人
    old_assignee_id = str(ticket.assignee_id) if ticket.assignee_id else None
    if data.assignee_id:
        assignee_result = await db.execute(select(User).where(User.id == data.assignee_id))
        assignee = assignee_result.scalar_one_or_none()
        if not assignee:
            raise HTTPException(status_code=404, detail="指派用户不存在")
        ticket.assignee_id = assignee.id
    else:
        ticket.assignee_id = None

    await db.commit()

    # 审计日志
    await audit_service.log(
        db=db,
        user_id=str(current_user.id),
        action="ticket.assign" if data.assignee_id else "ticket.unassign",
        resource_type="ticket",
        resource_id=str(ticket.id),
        old_value={"assignee_id": old_assignee_id},
        new_value={"assignee_id": data.assignee_id}
    )

    # 构建响应
    ...


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
async def change_ticket_status(
    ticket_id: str,
    data: ChangeStatusRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    audit_service: AuditService = Depends()
):
    """变更工单状态"""
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()

    if not ticket or ticket.deleted_at:
        raise HTTPException(status_code=404, detail="工单不存在")

    new_status = TicketStatus(data.status)
    old_status = ticket.status

    # 状态转换验证
    allowed_transitions = STATUS_TRANSITIONS.get(old_status.value, [])
    if new_status.value not in allowed_transitions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不允许的状态转换：从 {old_status.value} 到 {new_status.value}"
        )

    # 指派人检查：pending <-> in_progress, resolved <-> in_progress 需要是指派人
    if new_status.value in ["in_progress", "pending", "resolved"]:
        if current_user.role.value != "admin" and ticket.assignee_id != current_user.id:
            raise HTTPException(status_code=403, detail="只有指派人可以变更此状态")

    # closed 状态需要是创建者或管理员
    if new_status.value == "closed":
        if current_user.role.value != "admin" and ticket.creator_id != current_user.id:
            raise HTTPException(status_code=403, detail="只有创建者或管理员可以关闭工单")

    # 更新状态
    ticket.status = new_status
    await db.commit()

    # 记录状态历史
    history = TicketStatusHistory(
        ticket_id=ticket.id,
        from_status=old_status,
        to_status=new_status,
        changed_by_id=current_user.id
    )
    db.add(history)
    await db.commit()

    # 审计日志
    await audit_service.log(
        db=db,
        user_id=str(current_user.id),
        action="ticket.status_change",
        resource_type="ticket",
        resource_id=str(ticket.id),
        old_value={"status": old_status.value},
        new_value={"status": new_status.value}
    )

    # 构建响应
    ...
```

## 6. Service 层

### 6.1 app/services/audit_service.py

```python
"""审计日志服务"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.mysql import insert
from app.models.audit_log import AuditLog


class AuditService:
    """审计日志服务"""

    @staticmethod
    async def log(
        db: AsyncSession,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        old_value: dict | None = None,
        new_value: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> AuditLog:
        """记录审计日志"""
        import uuid

        log_entry = AuditLog(
            id=uuid.uuid4(),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(log_entry)
        await db.commit()
        await db.refresh(log_entry)
        return log_entry
```

## 7. 主应用入口

### 7.1 app/main.py

```python
"""FastAPI 应用入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.database import init_db
from app.api import auth, users, tickets, audit_logs

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """启动时初始化"""
    await init_db()


# 注册路由
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tickets.router)
app.include_router(audit_logs.router)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": settings.APP_VERSION}
```

## 8. 依赖包

### requirements.txt

```
# Core
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
pydantic-settings>=2.1.0

# Database
sqlalchemy>=2.0.25
aiomysql>=0.2.0
alembic>=1.13.0

# Auth
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6

# Utils
python-dotenv>=1.0.0
```
