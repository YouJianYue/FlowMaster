# -*- coding: utf-8 -*-

"""
菜单服务实现 - 数据库驱动版本
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from apps.common.config.database.database_session import DatabaseSession
from apps.system.core.model.entity.menu_entity import MenuEntity

logger = logging.getLogger(__name__)


class MenuServiceImpl:
    """菜单服务实现（数据库驱动）"""
    
    async def get_menu_tree(self, only_enabled: bool = True) -> List[Dict[str, Any]]:
        """
        获取菜单树（从数据库）
        
        Args:
            only_enabled: 是否仅获取启用的菜单
            
        Returns:
            List[Dict[str, Any]]: 菜单树数据
        """
        async with DatabaseSession.get_session_context() as session:
            # 构建查询条件
            query = select(MenuEntity).order_by(MenuEntity.sort, MenuEntity.id)
            
            if only_enabled:
                query = query.where(MenuEntity.status == 1)
            
            # 执行查询
            result = await session.execute(query)
            menus = result.scalars().all()
            
            # 转换为字典格式
            menu_list = []
            for menu in menus:
                menu_dict = {
                    "id": menu.id,
                    "title": menu.title,
                    "parent_id": menu.parent_id,
                    "type": menu.type,  # 保持整数类型
                    "path": menu.path,
                    "name": menu.name,
                    "component": menu.component,
                    "redirect": menu.redirect,
                    "icon": menu.icon,
                    "is_external": menu.is_external,
                    "is_cache": menu.is_cache,
                    "is_hidden": menu.is_hidden,
                    "permission": menu.permission,
                    "sort": menu.sort,
                    "status": menu.status,  # 保持整数类型
                    "create_user": menu.create_user,
                    "create_time": menu.create_time.strftime("%Y-%m-%d %H:%M:%S") if menu.create_time else None,  # 简单时间格式
                    "update_time": menu.update_time.strftime("%Y-%m-%d %H:%M:%S") if menu.update_time else None   # 简单时间格式
                }
                menu_list.append(menu_dict)
            
            # 构建树结构
            return self._build_tree(menu_list)
    
    async def get_user_menu_tree(self, user_id: int) -> List[Dict[str, Any]]:
        """
        获取用户权限菜单树
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[Dict[str, Any]]: 用户权限菜单树
        """
        # 目前假设所有用户都能看到所有菜单（简化实现）
        # 后续需要根据用户角色权限进行过滤
        menu_tree = await self.get_menu_tree(only_enabled=True)
        
        # 过滤掉隐藏菜单和按钮类型菜单（路由只需要目录和菜单）
        return self._filter_for_routes(menu_tree)
    
    def _build_tree(self, menu_list: List[Dict[str, Any]], parent_id: int = 0) -> List[Dict[str, Any]]:
        """
        构建菜单树结构
        
        Args:
            menu_list: 菜单数据列表
            parent_id: 父级ID
            
        Returns:
            List[Dict[str, Any]]: 树结构菜单数据
        """
        tree = []
        
        for menu in menu_list:
            if menu["parent_id"] == parent_id:
                # 递归构建子菜单
                children = self._build_tree(menu_list, menu["id"])
                if children:
                    menu["children"] = children
                tree.append(menu)
        
        # 按sort排序
        tree.sort(key=lambda x: x.get("sort", 999))
        
        return tree
    
    def _filter_for_routes(self, menu_tree: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        过滤菜单树，只保留路由需要的菜单（目录和菜单类型，排除按钮）
        
        Args:
            menu_tree: 菜单树数据
            
        Returns:
            List[Dict[str, Any]]: 过滤后的菜单树
        """
        result = []
        
        for menu in menu_tree:
            # 只保留目录(1)和菜单(2)类型，排除按钮(3)
            if menu.get("type") in [1, 2] and not menu.get("is_hidden", False):
                menu_copy = menu.copy()
                
                # 递归过滤子菜单
                if "children" in menu_copy:
                    filtered_children = self._filter_for_routes(menu_copy["children"])
                    if filtered_children:
                        menu_copy["children"] = filtered_children
                    else:
                        # 移除空的children字段
                        menu_copy.pop("children", None)
                
                result.append(menu_copy)
        
        return result
    
    def convert_to_frontend_format(self, menu_tree: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        转换为前端期望的格式（camelCase字段名）
        
        Args:
            menu_tree: 菜单树数据
            
        Returns:
            List[Dict[str, Any]]: 前端格式的菜单树
        """
        result = []
        
        for menu in menu_tree:
            # 转换字段名为camelCase（匹配参考项目接口格式）
            frontend_menu = {
                "id": menu.get("id"),
                "parentId": menu.get("parent_id"),
                "title": menu.get("title"),
                "sort": menu.get("sort"),
                "type": menu.get("type"),  # 保持整数类型
                "path": menu.get("path"),
                "name": menu.get("name"),
                "component": menu.get("component"),
                "redirect": menu.get("redirect"),
                "icon": menu.get("icon"),
                "isExternal": menu.get("is_external"),
                "isCache": menu.get("is_cache"),
                "isHidden": menu.get("is_hidden"),
                "permission": menu.get("permission"),
                "status": menu.get("status"),  # 保持整数类型
                "createUser": menu.get("create_user"),
                "createUserString": "超级管理员",  # 简化实现
                "createTime": menu.get("create_time"),  # 已经是正确格式
                "disabled": None  # 添加缺失的disabled字段
            }
            
            # 处理子菜单
            if "children" in menu:
                frontend_menu["children"] = self.convert_to_frontend_format(menu["children"])
            
            # 移除None值
            frontend_menu = {k: v for k, v in frontend_menu.items() if v is not None}
            
            result.append(frontend_menu)
        
        return result


# 全局服务实例
menu_service = MenuServiceImpl()