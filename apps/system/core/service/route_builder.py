# -*- coding: utf-8 -*-

"""
路由构建器 - 对应参考项目的路由树构建逻辑
"""

from typing import List, Dict, Any
from apps.system.core.model.entity.menu_entity import MenuEntity
from apps.system.core.model.resp.route_resp import RouteResp, RouteMetaResp
from apps.system.core.service.menu_service import MenuService
from apps.system.core.enums.menu_type_enum import MenuTypeEnum


class RouteBuilder:
    """
    路由构建器
    
    负责将菜单数据转换为前端路由配置
    对应参考项目中AuthServiceImpl.buildRouteTree()的逻辑
    """
    
    def __init__(self, menu_service: MenuService):
        """
        初始化路由构建器
        
        Args:
            menu_service: 菜单服务
        """
        self.menu_service = menu_service
    
    async def build_user_route_tree(self, user_id: int) -> List[RouteResp]:
        """
        构建用户路由树（完全对应参考项目逻辑）
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[RouteResp]: 用户路由树
        """
        # 1. 获取用户所有菜单（通过用户角色）
        user_menus = await self.menu_service.list_by_user_id(user_id)
        
        if not user_menus:
            return []
        
        # 2. 过滤掉按钮类型的菜单（路由中不包含按钮）
        route_menus = [
            menu for menu in user_menus 
            if menu.type != MenuTypeEnum.BUTTON and menu.is_visible()
        ]
        
        if not route_menus:
            return []
        
        # 3. 构建路由树
        return self._build_route_tree(route_menus)
    
    def _build_route_tree(self, menus: List[MenuEntity]) -> List[RouteResp]:
        """
        构建路由树结构
        
        Args:
            menus: 菜单列表
            
        Returns:
            List[RouteResp]: 路由树
        """
        if not menus:
            return []
        
        # 创建菜单映射
        menu_map = {menu.id: menu for menu in menus}
        
        # 构建树结构
        def build_children(parent_id: int) -> List[RouteResp]:
            children = []
            
            # 找出所有子菜单
            child_menus = [menu for menu in menus if menu.parent_id == parent_id]
            
            # 按排序字段排序
            child_menus.sort(key=lambda x: (x.sort, x.id))
            
            for menu in child_menus:
                # 转换为路由响应对象
                route = self._convert_menu_to_route(menu)
                
                # 递归构建子路由
                children_routes = build_children(menu.id)
                if children_routes:
                    route.children = children_routes
                
                children.append(route)
            
            return children
        
        # 构建根路由（parent_id = 0）
        return build_children(0)
    
    def _convert_menu_to_route(self, menu: MenuEntity) -> RouteResp:
        """
        将菜单实体转换为路由响应
        
        Args:
            menu: 菜单实体
            
        Returns:
            RouteResp: 路由响应
        """
        return RouteResp(
            id=menu.id,
            parent_id=menu.parent_id,
            type=menu.type.value if hasattr(menu.type, 'value') else str(menu.type),
            path=menu.path,
            name=menu.name,
            component=menu.component,
            redirect=menu.redirect,
            meta=RouteMetaResp(
                title=menu.title,
                icon=menu.icon,
                hidden=menu.is_hidden,
                cache=menu.is_cache,
                external=menu.is_external
            ),
            permission=menu.permission,
            sort=menu.sort
        )
    
    async def build_menu_options(self, user_id: int) -> List[Dict[str, Any]]:
        """
        构建菜单选项（用于前端菜单选择器等场景）
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[Dict[str, Any]]: 菜单选项
        """
        user_menus = await self.menu_service.list_by_user_id(user_id)
        
        if not user_menus:
            return []
        
        # 只包含目录和菜单类型
        menu_options = []
        for menu in user_menus:
            if menu.type in [MenuTypeEnum.DIR, MenuTypeEnum.MENU] and menu.is_visible():
                option = {
                    "value": menu.id,
                    "label": menu.title,
                    "type": menu.type.value if hasattr(menu.type, 'value') else str(menu.type),
                    "parent_id": menu.parent_id,
                    "sort": menu.sort
                }
                menu_options.append(option)
        
        # 按排序字段排序
        menu_options.sort(key=lambda x: (x['sort'], x['value']))
        
        return menu_options
    
    async def get_user_permissions(self, user_id: int) -> List[str]:
        """
        获取用户权限列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[str]: 权限列表
        """
        permissions = await self.menu_service.list_permission_by_user_id(user_id)
        return list(permissions)


# 依赖注入函数
def get_route_builder(menu_service: MenuService) -> RouteBuilder:
    """
    获取路由构建器实例
    
    Args:
        menu_service: 菜单服务
        
    Returns:
        RouteBuilder: 路由构建器实例
    """
    return RouteBuilder(menu_service)