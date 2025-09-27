# -*- coding: utf-8 -*-

"""
权限查询服务实现
实现根据用户ID查询权限的核心逻辑
"""

from typing import List, Set
from sqlalchemy import select, distinct

from apps.common.config.logging import get_logger
from apps.system.core.service.permission_service import PermissionService
from apps.system.core.model.entity.role_entity import RoleEntity
from apps.system.core.model.entity.menu_entity import MenuEntity
from apps.system.core.model.entity.user_role_entity import UserRoleEntity
from apps.system.core.model.entity.role_menu_entity import RoleMenuEntity
from apps.common.config.database.database_session import DatabaseSession

logger = get_logger(__name__)


class PermissionServiceImpl(PermissionService):
    """权限查询服务实现"""

    async def get_user_permissions(self, user_id: int) -> Set[str]:
        """
        根据用户ID获取用户权限码集合

        一比一复刻参考项目 RoleServiceImpl.listPermissionByUserId() 实现：
        1. 先获取用户角色编码集合
        2. 如果包含超级管理员角色，返回全部权限标识 "*:*:*"
        3. 否则调用 MenuService.listPermissionByUserId() 查询具体权限

        核心SQL逻辑（等价于参考项目的 MenuService.listPermissionByUserId）：
        SELECT DISTINCT m.permission FROM sys_menu m
        JOIN sys_role_menu rm ON m.id = rm.menu_id
        JOIN sys_user_role ur ON rm.role_id = ur.role_id
        WHERE ur.user_id = ? AND m.permission IS NOT NULL AND m.status = 1
        """
        try:
            logger.info(f"Getting permissions for user: {user_id}")

            # 一比一复刻参考项目逻辑：先获取用户角色编码集合
            role_codes = await PermissionServiceImpl._get_user_role_codes(user_id)

            # 一比一复刻参考项目：超级管理员赋予全部权限
            from apps.common.enums.role_code_enum import RoleCodeEnum
            if RoleCodeEnum.SUPER_ADMIN.value in role_codes:
                from apps.common.constant.global_constants import ALL_PERMISSION
                logger.info(f"用户 {user_id} 为超级管理员，返回全部权限")
                return {ALL_PERMISSION}

            # 一比一复刻参考项目：普通用户通过数据库查询获取具体权限
            async with DatabaseSession.get_session_context() as session:
                # 构建查询：用户 -> 角色 -> 菜单 -> 权限
                stmt = (
                    select(distinct(MenuEntity.permission))
                    .select_from(MenuEntity)
                    .join(RoleMenuEntity, MenuEntity.id == RoleMenuEntity.menu_id)
                    .join(
                        UserRoleEntity, RoleMenuEntity.role_id == UserRoleEntity.role_id
                    )
                    .where(
                        UserRoleEntity.user_id == user_id,
                        MenuEntity.permission.isnot(None),
                        MenuEntity.permission != "",
                        MenuEntity.status == 1,
                    )
                )

                result = await session.execute(stmt)
                permissions = {row[0] for row in result.fetchall() if row[0]}

                logger.info(
                    f"Found {len(permissions)} permissions for user {user_id}: {list(permissions)[:10]}..."
                )
                return permissions

        except Exception as e:
            logger.error(f"Failed to get user permissions: {e}")
            return set()

    @staticmethod
    async def _get_user_role_codes(user_id: int) -> Set[str]:
        """
        获取用户角色编码集合

        一比一复刻参考项目 RoleServiceImpl.listCodeByUserId() 实现
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 先获取用户关联的角色ID列表
                stmt = (
                    select(UserRoleEntity.role_id)
                    .where(UserRoleEntity.user_id == user_id)
                )

                result = await session.execute(stmt)
                role_ids = [row[0] for row in result.fetchall()]

                if not role_ids:
                    return set()

                # 根据角色ID获取角色编码
                stmt = (
                    select(RoleEntity.code)
                    .where(RoleEntity.id.in_(role_ids))
                )

                result = await session.execute(stmt)
                role_codes = {row[0] for row in result.fetchall() if row[0]}

                logger.debug(f"User {user_id} role codes: {role_codes}")
                return role_codes

        except Exception as e:
            logger.error(f"Failed to get user role codes: {e}")
            return set()

    async def get_user_roles(self, user_id: int) -> List[str]:
        """根据用户ID获取用户角色编码列表"""
        try:
            logger.info(f"Getting roles for user: {user_id}")
            role_codes = await PermissionServiceImpl._get_user_role_codes(user_id)
            return list(role_codes)

        except Exception as e:
            logger.error(f"Failed to get user roles: {e}")
            return []

    async def has_permission(self, user_id: int, permission: str) -> bool:
        """检查用户是否拥有指定权限"""
        permissions = await self.get_user_permissions(user_id)
        # 如果用户拥有全部权限，直接返回 True
        from apps.common.constant.global_constants import ALL_PERMISSION
        if ALL_PERMISSION in permissions:
            return True
        return permission in permissions

    async def has_any_permission(self, user_id: int, permissions: List[str]) -> bool:
        """检查用户是否拥有任意一个权限"""
        user_permissions = await self.get_user_permissions(user_id)
        # 如果用户拥有全部权限，直接返回 True
        from apps.common.constant.global_constants import ALL_PERMISSION
        if ALL_PERMISSION in user_permissions:
            return True
        return any(perm in user_permissions for perm in permissions)

    @staticmethod
    async def _get_all_permissions() -> Set[str]:
        """获取系统中所有权限（超级管理员使用）"""
        try:
            logger.info("Getting all system permissions for super admin")

            async with DatabaseSession.get_session_context() as session:
                stmt = select(distinct(MenuEntity.permission)).where(
                    MenuEntity.permission.isnot(None),
                    MenuEntity.permission != "",
                    MenuEntity.status == 1,
                )

                result = await session.execute(stmt)
                permissions = {row[0] for row in result.fetchall() if row[0]}

                logger.info(f"Found {len(permissions)} total system permissions")
                return permissions

        except Exception as e:
            logger.error(f"Failed to get all permissions: {e}")
            return set()

    async def get_user_menu_permissions(self, user_id: int) -> List[dict]:
        """
        获取用户菜单权限详细信息（包含菜单信息）
        用于前端权限控制和菜单显示
        """
        try:
            logger.info(f"Getting menu permissions for user: {user_id}")

            async with DatabaseSession.get_session_context() as session:
                # 一比一复刻参考项目：先检查是否为超级管理员
                role_codes = await PermissionServiceImpl._get_user_role_codes(user_id)
                from apps.common.enums.role_code_enum import RoleCodeEnum

                if RoleCodeEnum.SUPER_ADMIN.value in role_codes:
                    # 超级管理员获取所有菜单
                    stmt = select(MenuEntity).where(MenuEntity.status == 1)
                else:
                    # 普通用户根据角色获取菜单
                    stmt = (
                        select(MenuEntity)
                        .select_from(MenuEntity)
                        .join(RoleMenuEntity, MenuEntity.id == RoleMenuEntity.menu_id)
                        .join(
                            UserRoleEntity,
                            RoleMenuEntity.role_id == UserRoleEntity.role_id,
                        )
                        .where(
                            UserRoleEntity.user_id == user_id, MenuEntity.status == 1
                        )
                        .distinct()
                    )

                result = await session.execute(stmt)
                menus = result.scalars().all()

                menu_list = []
                for menu in menus:
                    menu_data = {
                        "id": menu.id,
                        "title": menu.title,
                        "name": menu.name,
                        "type": menu.type,
                        "permission": menu.permission,
                        "path": menu.path,
                        "component": menu.component,
                    }
                    menu_list.append(menu_data)

                logger.info(
                    f"Found {len(menu_list)} menu permissions for user {user_id}"
                )
                return menu_list

        except Exception as e:
            logger.error(f"Failed to get user menu permissions: {e}")
            return []