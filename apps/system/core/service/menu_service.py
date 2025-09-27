# -*- coding: utf-8 -*-

"""
菜单服务 - 对应参考项目的MenuService
"""

from abc import ABC, abstractmethod
from typing import List, Set, Dict, Any
from apps.system.core.model.resp.menu_resp import MenuResp


class MenuService(ABC):
    """
    菜单业务服务接口

    对应Java服务: MenuService
    提供菜单权限验证、用户菜单查询等功能
    """

    @abstractmethod
    async def get_menu_tree(self, only_enabled: bool = True) -> List[Dict[str, Any]]:
        """
        获取菜单树

        Args:
            only_enabled: 是否仅获取启用的菜单

        Returns:
            List[Dict[str, Any]]: 菜单树数据
        """
        pass

    @abstractmethod
    async def get_user_menu_tree(self, user_id: int) -> List[Dict[str, Any]]:
        """
        获取用户权限菜单树

        Args:
            user_id: 用户ID

        Returns:
            List[Dict[str, Any]]: 用户权限菜单树
        """
        pass

    @abstractmethod
    def convert_to_frontend_format(self, menu_tree: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        转换为前端期望的格式（camelCase字段名）

        Args:
            menu_tree: 菜单树数据

        Returns:
            List[Dict[str, Any]]: 前端格式的菜单树
        """
        pass

    @abstractmethod
    async def create_menu(self, menu_req: 'MenuReq') -> 'MenuResp':
        """
        创建菜单

        Args:
            menu_req: 菜单创建请求参数

        Returns:
            MenuResp: 创建的菜单数据
        """
        pass

    @abstractmethod
    async def update_menu(self, menu_id: int, menu_req: 'MenuReq') -> 'MenuResp':
        """
        更新菜单

        Args:
            menu_id: 菜单ID
            menu_req: 菜单更新请求参数

        Returns:
            MenuResp: 更新的菜单数据
        """
        pass

    @abstractmethod
    async def update_menu_status(self, menu_id: int, status: int) -> None:
        """
        更新菜单状态

        Args:
            menu_id: 菜单ID
            status: 状态值（1=启用，2=禁用）
        """
        pass

    @abstractmethod
    async def batch_delete_menu(self, ids: List[int]) -> None:
        """
        批量删除菜单

        Args:
            ids: 菜单ID列表
        """
        pass

    @abstractmethod
    async def get_menu_dict_tree(self) -> List[Dict[str, Any]]:
        """
        获取菜单字典树（用于下拉选择）

        Returns:
            List[Dict[str, Any]]: 菜单字典树数据
        """
        pass

    @abstractmethod
    async def clear_cache(self) -> None:
        """
        清除缓存
        """
        pass

    @abstractmethod
    async def list_all_menus(self) -> List[Dict[str, Any]]:
        """
        获取所有菜单数据

        Returns:
            List[Dict[str, Any]]: 菜单列表
        """
        pass

    @abstractmethod
    async def list_permission_by_user_id(self, user_id: int) -> Set[str]:
        """
        根据用户ID查询权限码集合

        Args:
            user_id: 用户ID

        Returns:
            Set[str]: 权限码集合
        """
        pass

    @abstractmethod
    async def list_by_user_id(self, user_id: int) -> List[Dict[str, Any]]:
        """
        根据用户ID查询菜单列表

        Args:
            user_id: 用户ID

        Returns:
            List[Dict[str, Any]]: 用户有权限的菜单列表
        """
        pass

    @abstractmethod
    async def get_user_route_tree(self, user_id: int) -> List[Dict[str, Any]]:
        """
        获取用户路由树（用于前端路由配置）

        Args:
            user_id: 用户ID

        Returns:
            List[Dict[str, Any]]: 用户路由树
        """
        pass

    @abstractmethod
    async def build_menu_tree_with_permissions(self, user_id: int) -> List[Dict[str, Any]]:
        """
        构建包含权限信息的菜单树

        Args:
            user_id: 用户ID

        Returns:
            List[Dict[str, Any]]: 菜单树（包含权限信息）
        """
        pass

    @abstractmethod
    def convert_to_route_format(self, menu_tree: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将菜单树转换为前端路由格式

        Args:
            menu_tree: 菜单树数据

        Returns:
            List[Dict[str, Any]]: 前端路由格式的菜单树
        """
        pass

    @abstractmethod
    async def get_permission_tree(self) -> List[Dict[str, Any]]:
        """
        获取权限树 - 用于角色权限分配

        Returns:
            List[Dict[str, Any]]: 权限树列表
        """
        pass


# 依赖注入函数
def get_menu_service() -> MenuService:
    """
    获取菜单服务实例（依赖注入）
    
    Args:
        
    Returns:
        MenuService: 菜单服务实例
    """
    from apps.system.core.service.impl.menu_service_impl import menu_service
    return menu_service
