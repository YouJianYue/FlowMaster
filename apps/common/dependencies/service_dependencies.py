# -*- coding: utf-8 -*-

"""
服务层依赖注入

统一管理所有服务层的依赖注入函数
"""

from apps.system.core.service.menu_service import MenuService
from apps.system.core.service.role_service import RoleService
from apps.system.core.service.user_role_service import UserRoleService


def get_menu_service() -> MenuService:
    """
    获取菜单服务实例（依赖注入）

    Returns:
        MenuService: 菜单服务实例
    """
    from apps.system.core.service.impl.menu_service_impl import menu_service
    return menu_service


def get_role_service() -> RoleService:
    """
    获取角色服务实例（依赖注入）

    Returns:
        RoleService: 角色服务实例
    """
    from apps.system.core.service.impl.role_service_impl import role_service
    return role_service


def get_user_role_service() -> UserRoleService:
    """
    获取用户角色服务实例（依赖注入）

    Returns:
        UserRoleService: 用户角色服务实例
    """
    from apps.system.core.service.impl.user_role_service_impl import user_role_service
    return user_role_service