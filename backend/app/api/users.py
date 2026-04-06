"""用户路由"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import hash_password
from app.models import User, UserRole
from app.api.deps import get_current_admin_user
from app.schemas.auth import UserBriefResponse, UserResponse
from app.schemas.base import BaseSchema
from pydantic import BaseModel, Field, EmailStr

router = APIRouter(prefix="/users", tags=["用户"])


class UpdateUserRequest(BaseModel):
    """更新用户请求"""
    role: str | None = Field(None, pattern="^(admin|user)$")
    is_active: bool | None = None


class CreateUserRequest(BaseSchema):
    """创建用户请求（管理员）"""
    username: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str = Field(default="user", pattern="^(admin|user)$")


@router.get("", response_model=list[UserBriefResponse])
async def list_users(
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表（管理员）"""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [
        UserBriefResponse(id=bytes(u.id).hex(), username=u.username)
        for u in users
    ]


@router.get("/all", response_model=list[UserResponse])
async def list_all_users(
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """获取完整用户列表（管理员）"""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [
        UserResponse(
            id=bytes(u.id).hex(),
            username=u.username,
            email=u.email,
            role=u.role.value,
            is_active=u.is_active,
            created_at=u.created_at
        )
        for u in users
    ]


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    data: UpdateUserRequest,
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户（角色/状态），仅管理员"""
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id).bytes))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 不能修改自己的角色/状态
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能修改自己的账户")

    if data.role is not None:
        user.role = UserRole(data.role)
    if data.is_active is not None:
        user.is_active = data.is_active

    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=bytes(user.id).hex(),
        username=user.username,
        email=user.email,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: CreateUserRequest,
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """创建用户（管理员）"""
    # 检查邮箱唯一
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该邮箱已被注册")

    # 检查用户名唯一
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该用户名已被使用")

    user = User(
        id=uuid.uuid4().bytes,
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        role=UserRole(data.role)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=bytes(user.id).hex(),
        username=user.username,
        email=user.email,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at
    )
