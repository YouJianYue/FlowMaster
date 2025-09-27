# -*- coding: utf-8 -*-
"""
权限控制装饰器

实现类似 Java @SaCheckPermission 的权限验证功能
@author: FlowMaster
@since: 2025/9/18
"""

from functools import wraps
from typing import Callable, Union, List
from fastapi import HTTPException, status, Request, Depends
from apps.common.context.user_context_holder import UserContextHolder
from apps.system.core.service.menu_service import get_menu_service
from apps.common.config.logging.logging_config import get_logger

logger = get_logger(__name__)


class PermissionChecker:
    """权限检查器 - 实现类似 SaCheckPermission 的功能"""

    @staticmethod
    async def check_permission(permission: Union[str, List[str]], require_all: bool = True) -> bool:
        """
        检查当前用户是否具有指定权限

        Args:
            permission: 权限标识或权限列表
            require_all: 是否需要全部权限 (True=AND逻辑, False=OR逻辑)

        Returns:
            bool: 是否有权限
        """
        try:
            # 获取当前用户上下文
            user_context = UserContextHolder.get_context()
            if not user_context:
                logger.warning("权限检查失败: 用户上下文为空")
                return False

            # 超级管理员拥有所有权限
            if user_context.is_super_admin:
                logger.debug(f"超级管理员 {user_context.username} 通过权限检查: {permission}")
                return True

            # 获取用户权限列表
            menu_service = get_menu_service()
            user_permissions = await menu_service.list_permission_by_user_id(user_context.id)

            # 转换为权限集合
            user_permission_set = set(user_permissions)

            # 处理权限检查
            if isinstance(permission, str):
                # 单个权限检查
                has_permission = permission in user_permission_set
                logger.debug(f"用户 {user_context.username} 权限检查 [{permission}]: {'通过' if has_permission else '拒绝'}")
                return has_permission

            elif isinstance(permission, list):
                # 多个权限检查
                if require_all:
                    # AND逻辑 - 需要全部权限
                    has_all = all(perm in user_permission_set for perm in permission)
                    logger.debug(f"用户 {user_context.username} 权限检查 [ALL:{permission}]: {'通过' if has_all else '拒绝'}")
                    return has_all
                else:
                    # OR逻辑 - 需要任一权限
                    has_any = any(perm in user_permission_set for perm in permission)
                    logger.debug(f"用户 {user_context.username} 权限检查 [ANY:{permission}]: {'通过' if has_any else '拒绝'}")
                    return has_any

            return False

        except Exception as e:
            logger.error(f"权限检查异常: {e}")
            return False


def require_permission(permission: Union[str, List[str]], require_all: bool = True):
    """
    权限控制装饰器 - 类似 Java @SaCheckPermission

    Args:
        permission: 权限标识或权限列表
        require_all: 是否需要全部权限 (True=AND逻辑, False=OR逻辑)

    Usage:
        @require_permission("system:role:list")
        async def list_roles():
            pass

        @require_permission(["system:role:list", "system:role:create"], require_all=False)
        async def manage_roles():
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 执行权限检查
            has_permission = await PermissionChecker.check_permission(permission, require_all)

            if not has_permission:
                # 构建错误信息
                perm_str = permission if isinstance(permission, str) else str(permission)
                user_context = UserContextHolder.get_context()
                username = user_context.username if user_context else "未知用户"

                logger.warning(f"权限拒绝: 用户 {username} 访问 {func.__name__} 缺少权限 {perm_str}")

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "message": "权限不足",
                        "code": 403,
                        "data": None,
                        "timestamp": None,
                        "required_permission": perm_str
                    }
                )

            # 权限验证通过，执行原函数
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_any_permission(*permissions: str):
    """
    需要任一权限的装饰器 - OR逻辑

    Args:
        *permissions: 权限标识列表

    Usage:
        @require_any_permission("system:role:list", "system:role:create")
        async def some_function():
            pass
    """
    return require_permission(list(permissions), require_all=False)


def require_all_permissions(*permissions: str):
    """
    需要全部权限的装饰器 - AND逻辑

    Args:
        *permissions: 权限标识列表

    Usage:
        @require_all_permissions("system:role:list", "system:role:create")
        async def some_function():
            pass
    """
    return require_permission(list(permissions), require_all=True)


# FastAPI 依赖注入形式的权限检查
async def check_permission_dependency(permission: str):
    """
    权限检查依赖 - 用于 FastAPI 的 Depends

    Usage:
        @router.get("/roles")
        async def list_roles(
            _: None = Depends(lambda: check_permission_dependency("system:role:list"))
        ):
            pass
    """
    has_permission = await PermissionChecker.check_permission(permission)
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "权限不足", "required_permission": permission}
        )
    return True