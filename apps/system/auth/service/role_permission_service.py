# -*- coding: utf-8 -*-

"""
权限查询服务 - 完全复刻参考项目的RoleService
"""

from typing import Set
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from apps.common.config.database.database_session import DatabaseSession
from apps.system.core.model.entity.role_entity import RoleEntity
from apps.system.core.model.entity.menu_entity import MenuEntity
from apps.system.core.model.entity.user_role_entity import UserRoleEntity
from apps.system.core.model.entity.role_menu_entity import RoleMenuEntity
from apps.common.context.role_context import RoleContext


class RolePermissionService:
    """
    角色权限服务

    复刻参考项目的RoleService中的权限相关方法
    """

    @staticmethod
    async def list_permission_by_user_id(user_id: int) -> Set[str]:
        """
        根据用户ID查询权限码集合

        完全复刻参考项目的 RoleService.listPermissionByUserId() 方法

        🔥 添加租户隔离过滤

        Args:
            user_id: 用户ID

        Returns:
            权限码集合
        """
        from apps.common.context.tenant_context_holder import TenantContextHolder

        permissions = set()

        async with DatabaseSession.get_session_context() as session:
            # 🔥 构建查询用户角色的语句，添加租户隔离
            role_stmt = select(UserRoleEntity.role_id).where(UserRoleEntity.user_id == user_id)

            # 🔥 一比一复刻参考项目：添加租户隔离过滤
            if TenantContextHolder.isTenantEnabled():
                tenant_id = TenantContextHolder.getTenantId()
                if tenant_id is not None:
                    role_stmt = role_stmt.where(UserRoleEntity.tenant_id == tenant_id)

            role_result = await session.execute(role_stmt)
            role_ids = [row[0] for row in role_result.fetchall()]

            if not role_ids:
                return permissions

            # 查询角色关联的菜单权限
            # 复刻参考项目的SQL逻辑：
            # SELECT DISTINCT m.permission FROM sys_menu m
            # JOIN sys_role_menu rm ON m.id = rm.menu_id
            # WHERE rm.role_id IN (role_ids) AND m.permission IS NOT NULL AND m.status = 1
            menu_stmt = (
                select(MenuEntity.permission)
                .join(RoleMenuEntity, MenuEntity.id == RoleMenuEntity.menu_id)
                .where(
                    and_(
                        RoleMenuEntity.role_id.in_(role_ids),
                        MenuEntity.permission.isnot(None),
                        MenuEntity.permission != '',
                        MenuEntity.status == 1  # 启用状态
                    )
                )
                .distinct()
            )

            menu_result = await session.execute(menu_stmt)
            for row in menu_result.fetchall():
                permission = row[0]
                if permission and permission.strip():
                    permissions.add(permission.strip())

        return permissions

    @staticmethod
    async def list_by_user_id(user_id: int) -> Set[RoleContext]:
        """
        根据用户ID查询角色信息集合

        完全复刻参考项目的 RoleService.listByUserId() 方法

        🔥 添加租户隔离过滤

        Args:
            user_id: 用户ID

        Returns:
            角色信息集合
        """
        from apps.common.context.tenant_context_holder import TenantContextHolder

        roles = set()

        async with DatabaseSession.get_session_context() as session:
            # 查询用户的角色信息
            # 复刻参考项目的SQL逻辑：
            # SELECT r.* FROM sys_role r
            # JOIN sys_user_role ur ON r.id = ur.role_id
            # WHERE ur.user_id = ?
            role_stmt = (
                select(RoleEntity)
                .join(UserRoleEntity, RoleEntity.id == UserRoleEntity.role_id)
                .where(UserRoleEntity.user_id == user_id)
            )

            # 🔥 一比一复刻参考项目：添加租户隔离过滤
            if TenantContextHolder.isTenantEnabled():
                tenant_id = TenantContextHolder.getTenantId()
                if tenant_id is not None:
                    # 同时过滤RoleEntity和UserRoleEntity的tenant_id
                    role_stmt = role_stmt.where(
                        and_(
                            RoleEntity.tenant_id == tenant_id,
                            UserRoleEntity.tenant_id == tenant_id
                        )
                    )

            role_result = await session.execute(role_stmt)
            role_entities = role_result.scalars().all()

            for role in role_entities:
                role_context = RoleContext(
                    id=role.id,
                    name=role.name,
                    code=role.code
                )
                roles.add(role_context)

        return roles