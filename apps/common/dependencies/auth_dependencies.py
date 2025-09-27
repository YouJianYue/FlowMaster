# -*- coding: utf-8 -*-

"""
认证相关依赖注入
"""

from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from apps.common.context.user_context import UserContext
from apps.common.context.user_context_holder import UserContextHolder
from apps.system.auth.service.auth_service_manager import get_auth_service
from apps.system.auth.service.auth_service import AuthService

# HTTP Bearer 认证
security = HTTPBearer()


def get_current_user() -> UserContext:
    """
    获取当前登录用户 - FastAPI 依赖项

    Returns:
        UserContext: 当前用户上下文

    Raises:
        HTTPException: 用户未登录时抛出 401 错误
    """
    user_context = UserContextHolder.get_context()
    if not user_context:
        raise HTTPException(status_code=401, detail="用户未登录")
    return user_context


def get_current_user_optional() -> Optional[UserContext]:
    """
    获取当前登录用户（可选） - FastAPI 依赖项
    适用于某些接口既支持登录用户也支持匿名用户的场景

    Returns:
        Optional[UserContext]: 当前用户上下文，未登录时返回 None
    """
    return UserContextHolder.get_context()


def get_current_user_id() -> int:
    """
    获取当前登录用户ID - FastAPI 依赖项

    Returns:
        int: 当前用户ID

    Raises:
        HTTPException: 用户未登录时抛出 401 错误
    """
    user_context = get_current_user()
    return user_context.id


def require_super_admin() -> UserContext:
    """
    要求超级管理员权限 - FastAPI 依赖项

    Returns:
        UserContext: 当前用户上下文

    Raises:
        HTTPException: 用户未登录或非超级管理员时抛出错误
    """
    user_context = get_current_user()
    if not user_context.is_super_admin:
        raise HTTPException(status_code=403, detail="需要超级管理员权限")
    return user_context


def get_auth_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    获取认证令牌 - FastAPI 依赖项

    Args:
        credentials: HTTP Bearer 认证凭据

    Returns:
        str: JWT 令牌
    """
    return credentials.credentials


def get_auth_service_dep() -> AuthService:
    """
    获取认证服务实例 - FastAPI 依赖项

    Returns:
        AuthService: 认证服务实例
    """
    return get_auth_service()