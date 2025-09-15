# -*- coding: utf-8 -*-

"""
权限初始化服务
为系统创建基础的角色和权限关联数据
"""

import logging
from typing import List, Dict, Any
from sqlalchemy import select, and_, insert
from sqlalchemy.exc import IntegrityError

from apps.system.core.model.entity.role_entity import RoleEntity
from apps.system.core.model.entity.menu_entity import MenuEntity  
from apps.system.core.model.entity.user_role_entity import UserRoleEntity
from apps.system.core.model.entity.role_menu_entity import RoleMenuEntity
from apps.common.config.database.database_session import DatabaseSession

logger = logging.getLogger(__name__)


class PermissionInitService:
    """权限初始化服务"""
    
    async def init_permissions(self):
        """初始化权限体系 - 创建超级管理员角色和权限关联"""
        try:
            logger.info("开始初始化权限体系...")
            
            async with DatabaseSession.get_session_context() as session:
                # 1. 检查并创建超级管理员角色
                super_admin_role_id = await self._ensure_super_admin_role(session)
                
                # 2. 为超级管理员角色分配所有菜单权限
                await self._assign_all_menus_to_super_admin(session, super_admin_role_id)
                
                # 3. 为用户ID=1分配超级管理员角色
                await self._assign_super_admin_role_to_user(session, 1, super_admin_role_id)
                
                await session.commit()
                logger.info("权限体系初始化完成")
                
        except Exception as e:
            logger.error(f"权限体系初始化失败: {e}")
            raise
    
    async def _ensure_super_admin_role(self, session) -> int:
        """确保超级管理员角色存在"""
        try:
            # 检查是否已存在超级管理员角色
            stmt = select(RoleEntity).where(RoleEntity.code == "SUPER_ADMIN")
            result = await session.execute(stmt)
            role = result.scalars().first()
            
            if role:
                logger.info(f"超级管理员角色已存在: {role.id}")
                return role.id
            
            # 创建超级管理员角色
            new_role = RoleEntity(
                name="超级管理员",
                code="SUPER_ADMIN",
                data_scope="ALL",
                description="拥有系统所有权限",
                sort=1,
                is_system=True,
                status=1
            )
            
            session.add(new_role)
            await session.flush()  # 获取生成的ID
            
            logger.info(f"创建超级管理员角色: {new_role.id}")
            return new_role.id
            
        except Exception as e:
            logger.error(f"创建超级管理员角色失败: {e}")
            raise
    
    async def _assign_all_menus_to_super_admin(self, session, role_id: int):
        """为超级管理员角色分配所有菜单权限"""
        try:
            # 获取所有启用的菜单
            stmt = select(MenuEntity.id).where(MenuEntity.status == 1)
            result = await session.execute(stmt)
            menu_ids = [row[0] for row in result.fetchall()]
            
            if not menu_ids:
                logger.warning("没有找到可用的菜单")
                return
            
            # 检查已存在的关联
            existing_stmt = select(RoleMenuEntity.menu_id).where(RoleMenuEntity.role_id == role_id)
            existing_result = await session.execute(existing_stmt)
            existing_menu_ids = {row[0] for row in existing_result.fetchall()}
            
            # 找到需要新增的关联
            new_menu_ids = [mid for mid in menu_ids if mid not in existing_menu_ids]
            
            if new_menu_ids:
                # 批量插入角色菜单关联
                role_menu_data = [
                    {"role_id": role_id, "menu_id": menu_id}
                    for menu_id in new_menu_ids
                ]
                
                await session.execute(insert(RoleMenuEntity), role_menu_data)
                logger.info(f"为超级管理员角色分配 {len(new_menu_ids)} 个菜单权限")
            else:
                logger.info("超级管理员角色已拥有所有菜单权限")
                
        except Exception as e:
            logger.error(f"分配菜单权限失败: {e}")
            raise
    
    async def _assign_super_admin_role_to_user(self, session, user_id: int, role_id: int):
        """为用户分配超级管理员角色"""
        try:
            # 检查是否已存在关联
            stmt = select(UserRoleEntity).where(
                and_(UserRoleEntity.user_id == user_id, UserRoleEntity.role_id == role_id)
            )
            result = await session.execute(stmt)
            existing = result.scalars().first()
            
            if existing:
                logger.info(f"用户 {user_id} 已拥有超级管理员角色")
                return
            
            # 创建用户角色关联
            user_role = UserRoleEntity(
                user_id=user_id,
                role_id=role_id
            )
            
            session.add(user_role)
            logger.info(f"为用户 {user_id} 分配超级管理员角色")
            
        except Exception as e:
            logger.error(f"分配用户角色失败: {e}")
            raise
    
    async def get_permission_stats(self) -> Dict[str, Any]:
        """获取权限统计信息"""
        try:
            async with DatabaseSession.get_session_context() as session:
                stats = {}
                
                # 统计角色数量
                role_stmt = select(RoleEntity.id).where(RoleEntity.status == 1)
                role_result = await session.execute(role_stmt)
                stats["roles_count"] = len(role_result.fetchall())
                
                # 统计菜单数量
                menu_stmt = select(MenuEntity.id).where(MenuEntity.status == 1)
                menu_result = await session.execute(menu_stmt)
                stats["menus_count"] = len(menu_result.fetchall())
                
                # 统计有权限标识的菜单数量
                perm_stmt = select(MenuEntity.id).where(
                    and_(MenuEntity.status == 1, MenuEntity.permission.isnot(None))
                )
                perm_result = await session.execute(perm_stmt)
                stats["permission_menus_count"] = len(perm_result.fetchall())
                
                # 统计用户角色关联
                user_role_stmt = select(UserRoleEntity.id)
                user_role_result = await session.execute(user_role_stmt)
                stats["user_role_relations"] = len(user_role_result.fetchall())
                
                # 统计角色菜单关联
                role_menu_stmt = select(RoleMenuEntity.id)
                role_menu_result = await session.execute(role_menu_stmt)
                stats["role_menu_relations"] = len(role_menu_result.fetchall())
                
                return stats
                
        except Exception as e:
            logger.error(f"获取权限统计失败: {e}")
            return {}


# 单例实例
permission_init_service = PermissionInitService()