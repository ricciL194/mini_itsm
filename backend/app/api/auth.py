"""认证路由"""
import uuid
from datetime import datetime, timedelta
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
from app.core.config import settings
from app.models import User, RefreshToken, UserRole
from app.schemas import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    TokenResponse,
    LogoutRequest,
    MessageResponse,
    UserResponse
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
        id=uuid.uuid4().bytes,
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return RegisterResponse(
        id=bytes(user.id).hex(),
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
    user_id_str = bytes(user.id).hex()
    access_token = create_access_token(user_id_str, user.role.value if isinstance(user.role, UserRole) else str(user.role))
    refresh_token_str, token_id = create_refresh_token(user_id_str)

    # 存储 Refresh Token
    db_refresh_token = RefreshToken(
        id=uuid.uuid4().bytes,
        user_id=user.id,
        token_id=token_id,
        expires_at=datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("user-agent", "")[:500]
    )
    db.add(db_refresh_token)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
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
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id).bytes))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )

    # 生成新 Token
    new_access_token = create_access_token(bytes(user.id).hex(), user.role.value if isinstance(user.role, UserRole) else str(user.role))
    new_refresh_token_str, new_token_id = create_refresh_token(bytes(user.id).hex())

    # 存储新 Refresh Token
    new_db_token = RefreshToken(
        id=uuid.uuid4().bytes,
        user_id=user.id,
        token_id=new_token_id,
        expires_at=datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("user-agent", "")[:500]
    )
    db.add(new_db_token)
    await db.commit()

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token_str,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    data: LogoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """用户登出"""
    if data.refresh_token:
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


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return UserResponse(
        id=bytes(current_user.id).hex(),
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.value if isinstance(current_user.role, UserRole) else str(current_user.role),
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )
