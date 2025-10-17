# -*- coding: utf-8 -*-

"""
套餐和菜单关联业务实现 - 一比一复刻PackageMenuServiceImpl

@author: continew-admin
@since: 2025/7/13 20:45
"""

from typing import List
from sqlalchemy import select, delete
from apps.common.config.database.database_session import DatabaseSession
from apps.system.tenant.service.package_menu_service import PackageMenuService
from apps.system.tenant.model.entity.package_menu_entity import PackageMenuEntity


class PackageMenuServiceImpl(PackageMenuService):
    """套餐和菜单关联业务实现"""

    async def add(self, menu_ids: List[int], package_id: int) -> bool:
        """
        新增套餐菜单关联

        一比一复刻参考项目PackageMenuServiceImpl.add()逻辑:
        1. 查询旧的菜单ID列表
        2. 对比新旧列表，如果没有变更则返回False
        3. 删除旧的关联
        4. 插入新的关联

        Args:
            menu_ids: 菜单ID列表
            package_id: 套餐ID

        Returns:
            bool: 是否成功（True：成功；False：无变更/失败）
        """
        async with DatabaseSession.get_session_context() as session:
            # 1. 查询旧的菜单ID列表
            old_menu_ids_query = select(PackageMenuEntity.menu_id).where(
                PackageMenuEntity.package_id == package_id
            )
            result = await session.execute(old_menu_ids_query)
            old_menu_ids = [row[0] for row in result.fetchall()]

            # 2. 对比新旧列表，如果没有变更则返回False
            # 一比一复刻: CollUtil.isEmpty(CollUtil.disjunction(menuIds, oldMenuIdList))
            # disjunction = 对称差集（在A不在B + 在B不在A）
            old_set = set(old_menu_ids)
            new_set = set(menu_ids) if menu_ids else set()
            symmetric_diff = old_set.symmetric_difference(new_set)

            if not symmetric_diff:  # 如果对称差集为空，说明没有变更
                return False

            # 3. 删除旧的关联
            delete_query = delete(PackageMenuEntity).where(
                PackageMenuEntity.package_id == package_id
            )
            await session.execute(delete_query)

            # 4. 插入新的关联
            if menu_ids:
                new_associations = [
                    PackageMenuEntity(package_id=package_id, menu_id=menu_id)
                    for menu_id in menu_ids
                ]
                session.add_all(new_associations)

            await session.commit()
            return True

    async def list_menu_ids_by_package_id(self, package_id: int) -> List[int]:
        """
        根据套餐ID查询菜单ID列表

        Args:
            package_id: 套餐ID

        Returns:
            List[int]: 菜单ID列表
        """
        async with DatabaseSession.get_session_context() as session:
            query = select(PackageMenuEntity.menu_id).where(
                PackageMenuEntity.package_id == package_id
            )
            result = await session.execute(query)
            return [row[0] for row in result.fetchall()]


# 全局服务实例
package_menu_service = PackageMenuServiceImpl()
