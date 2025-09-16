# -*- coding: utf-8 -*-

"""
菜单服务 - 对应参考项目的MenuService
"""

from typing import List, Set, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from apps.system.core.model.entity.menu_entity import MenuEntity
from apps.system.core.data.menu_initial_data import get_menu_data, build_menu_tree, filter_visible_menus


class MenuService:
    """
    菜单业务服务
    
    对应Java服务: MenuService
    提供菜单权限验证、用户菜单查询等功能
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        初始化菜单服务
        
        Args:
            db_session: 数据库会话（可选，为None时使用默认测试数据）
        """
        self.db = db_session
        # 加载菜单数据
        self._menu_data = get_menu_data()
    
    async def list_all_menus(self) -> List[Dict[str, Any]]:
        """
        获取所有菜单数据
        
        Returns:
            List[Dict[str, Any]]: 菜单列表
        """
        return self._menu_data.copy()
    
    async def list_permission_by_user_id(self, user_id: int) -> Set[str]:
        """
        根据用户ID查询权限码集合
        
        Args:
            user_id: 用户ID
            
        Returns:
            Set[str]: 权限码集合
        """
        # 如果有数据库会话，从数据库查询
        if self.db is not None:
            # TODO: 实现数据库查询逻辑
            # SELECT DISTINCT m.permission FROM sys_menu m 
            # JOIN sys_role_menu rm ON m.id = rm.menu_id 
            # JOIN sys_user_role ur ON rm.role_id = ur.role_id 
            # WHERE ur.user_id = ? AND m.permission IS NOT NULL AND m.status = 1
            pass
        
        # 使用默认测试数据 - 假设用户ID=1是超级管理员
        if user_id == 1:
            # 超级管理员拥有所有权限
            permissions = set()
            for menu in self._menu_data:
                if menu.get("permission") and menu.get("status") == 1:
                    permissions.add(menu["permission"])
            return permissions
        
        # 其他用户返回基础权限
        return {"system:user:list", "system:role:list", "system:menu:list"}
    
    async def list_by_user_id(self, user_id: int) -> List[Dict[str, Any]]:
        """
        根据用户ID查询菜单列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[Dict[str, Any]]: 用户有权限的菜单列表
        """
        # 如果有数据库会话，从数据库查询
        if self.db is not None:
            # TODO: 实现数据库查询逻辑
            pass
        
        # 使用默认测试数据 - 假设用户ID=1是超级管理员
        if user_id == 1:
            # 超级管理员拥有所有启用的菜单
            return [menu for menu in self._menu_data if menu.get("status") == 1]
        
        # 其他用户返回基础菜单
        basic_menu_ids = {1000, 1010, 1030, 1050}  # 系统管理及其子菜单
        return [menu for menu in self._menu_data 
                if menu.get("id") in basic_menu_ids and menu.get("status") == 1]
    
    async def get_user_route_tree(self, user_id: int) -> List[Dict[str, Any]]:
        """
        获取用户路由树（用于前端路由配置）
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[Dict[str, Any]]: 用户路由树
        """
        # 获取用户菜单
        user_menus = await self.list_by_user_id(user_id)
        
        # 过滤可见菜单（排除按钮类型，只保留目录和菜单）
        visible_menus = []
        for menu in user_menus:
            if (menu.get("status") == 1 and 
                not menu.get("is_hidden", False) and 
                menu.get("type") in [1, 2]):  # 1=目录, 2=菜单
                visible_menus.append(menu)
        
        # 构建树结构
        return build_menu_tree(visible_menus)
    
    async def build_menu_tree_with_permissions(self, user_id: int) -> List[Dict[str, Any]]:
        """
        构建包含权限信息的菜单树
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[Dict[str, Any]]: 菜单树（包含权限信息）
        """
        # 获取用户所有菜单
        user_menus = await self.list_by_user_id(user_id)
        
        # 构建完整树结构（包含按钮权限）
        return build_menu_tree(user_menus)
    
    def convert_to_route_format(self, menu_tree: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将菜单树转换为前端路由格式（匹配参考项目格式）
        
        Args:
            menu_tree: 菜单树数据
            
        Returns:
            List[Dict[str, Any]]: 前端路由格式的菜单树（完全匹配参考项目）
        """
        routes = []
        
        for menu in menu_tree:
            # 跳过按钮类型
            if menu.get("type") == 3:
                continue
                
            # 使用参考项目的完全一致的字段格式
            route = {
                "id": menu.get("id"),
                "parentId": menu.get("parent_id"), 
                "title": menu.get("title"),
                "type": menu.get("type"),
                "path": menu.get("path"),
                "name": menu.get("name"),
                "component": menu.get("component"),
                "icon": menu.get("icon"),
                "isExternal": menu.get("is_external", False),
                "isCache": menu.get("is_cache", False),
                "isHidden": menu.get("is_hidden", False),
                "sort": menu.get("sort", 999)
            }
            
            # 处理重定向
            if menu.get("redirect"):
                route["redirect"] = menu["redirect"]
                
            # 处理权限标识
            if menu.get("permission"):
                route["permission"] = menu["permission"]
            
            # 递归处理子菜单
            if menu.get("children"):
                route["children"] = self.convert_to_route_format(menu["children"])
            
            # 清理空值
            route = {k: v for k, v in route.items() if v is not None}
            
            routes.append(route)
        
        return routes

    async def get_permission_tree(self) -> List[Dict[str, Any]]:
        """
        获取权限树 - 用于角色权限分配

        Returns:
            List[Dict[str, Any]]: 权限树列表
        """
        # 获取所有菜单数据
        all_menus = await self.list_all_menus()

        # 构建权限树（包含所有菜单和按钮）
        permission_tree = []

        def build_tree_node(menu):
            return {
                "id": menu.get("id"),
                "parentId": menu.get("parent_id", 0),
                "title": menu.get("title"),
                "type": menu.get("type"),
                "permission": menu.get("permission", ""),
                "sort": menu.get("sort", 999),
                "children": []
            }

        # 创建节点映射
        node_map = {}
        root_nodes = []

        # 首先创建所有节点
        for menu in all_menus:
            node = build_tree_node(menu)
            node_map[menu["id"]] = node

            if menu.get("parent_id", 0) == 0:
                root_nodes.append(node)

        # 然后建立父子关系
        for menu in all_menus:
            parent_id = menu.get("parent_id", 0)
            if parent_id != 0 and parent_id in node_map:
                node_map[parent_id]["children"].append(node_map[menu["id"]])

        # 按排序号排序
        def sort_tree(nodes):
            nodes.sort(key=lambda x: x["sort"])
            for node in nodes:
                if node["children"]:
                    sort_tree(node["children"])

        sort_tree(root_nodes)
        return root_nodes


# 依赖注入函数
def get_menu_service(db_session: Optional[Session] = None) -> MenuService:
    """
    获取菜单服务实例（依赖注入）
    
    Args:
        db_session: 数据库会话
        
    Returns:
        MenuService: 菜单服务实例
    """
    return MenuService(db_session)