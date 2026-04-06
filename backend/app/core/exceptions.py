"""自定义异常"""
from fastapi import HTTPException, status


class AuthException(HTTPException):
    """认证异常"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(HTTPException):
    """权限不足异常"""
    def __init__(self, detail: str = "权限不足"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class NotFoundException(HTTPException):
    """资源不存在异常"""
    def __init__(self, detail: str = "资源不存在"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class BadRequestException(HTTPException):
    """请求错误异常"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
