"""安全工具：JWT + 密码哈希"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple, Union

from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

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
    expires_delta: Optional[timedelta] = None
) -> str:
    """创建 Access Token"""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: Dict[str, Any] = {
        "sub": user_id,
        "type": "access",
        "role": role,
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp())
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> Tuple[str, str]:
    """创建 Refresh Token，返回 (token, token_id)"""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    token_id = str(uuid.uuid4())

    to_encode: Dict[str, Any] = {
        "sub": user_id,
        "type": "refresh",
        "jti": token_id,
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp())
    }
    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, token_id


def decode_token(token: str) -> Optional[Dict[str, Any]]:
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


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """验证 Access Token"""
    payload = decode_token(token)
    if payload and payload.get("type") == "access":
        return payload
    return None


def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """验证 Refresh Token"""
    payload = decode_token(token)
    if payload and payload.get("type") == "refresh":
        return payload
    return None
