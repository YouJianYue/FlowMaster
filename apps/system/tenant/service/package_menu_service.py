# -*- coding: utf-8 -*-

"""
套餐和菜单关联业务接口 - 一比一复刻PackageMenuService

@author: continew-admin
@since: 2025/7/13 20:44
"""

from typing import List
from abc import ABC, abstractmethod


class PackageMenuService(ABC):
    """套餐和菜单关联业务接口"""

    @abstractmethod
    async def add(self, menu_ids: List[int], package_id: int) -> bool:
        """
        新增套餐菜单关联

        Args:
            menu_ids: 菜单ID列表
            package_id: 套餐ID

        Returns:
            bool: 是否成功（True：成功；False：无变更/失败）
        """
        pass

    @abstractmethod
    async def list_menu_ids_by_package_id(self, package_id: int) -> List[int]:
        """
        根据套餐ID查询菜单ID列表

        Args:
            package_id: 套餐ID

        Returns:
            List[int]: 菜单ID列表
        """
        pass
