# -*- coding: utf-8 -*-

"""
菜单服务 - 对应参考项目的MenuService
"""

from typing import List, Set, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from apps.system.core.model.entity.menu_entity import MenuEntity
from apps.system.core.model.entity.role_menu_entity import RoleMenuEntity
from apps.system.core.model.entity.user_role_entity import UserRoleEntity
from apps.system.core.model.data.default_rbac import (
    MENU_DATA_DICT, ROLE_MENU_DATA, USER_ROLE_DATA, ROLE_DATA_DICT
)
from apps.common.enums.dis_enable_status_enum import DisEnableStatusEnum
from apps.system.core.enums.menu_type_enum import MenuTypeEnum


class MenuService:
    """
    菜单业务服务
    
    对应Java服务: MenuService
    提供菜单权限验证、用户菜单查询等功能
    """
    
    def __init__(self, db_session: Optional[Session]):
        """
        初始化菜单服务
        
        Args:
            db_session: 数据库会话（可选，为None时使用默认测试数据）
        """
        self.db = db_session
    
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
            # WHERE ur.user_id = ? AND m.permission IS NOT NULL AND m.status = 'ENABLE'
            pass
        
        # 使用默认测试数据
        user_roles = [ur.role_id for ur in USER_ROLE_DATA if ur.user_id == user_id]
        if not user_roles:
            return set()
        
        # 检查是否为超级管理员
        super_admin_role = ROLE_DATA_DICT.get(1)  # ID=1的超级管理员角色
        if super_admin_role and 1 in user_roles:
            # 超级管理员拥有所有权限
            all_permissions = set()
            for menu in MENU_DATA_DICT.values():
                if (menu.permission and 
                    menu.permission.strip() and 
                    menu.status == DisEnableStatusEnum.ENABLE):
                    all_permissions.add(menu.permission)
            return all_permissions
        
        # 普通用户根据角色获取权限
        role_menus = [rm.menu_id for rm in ROLE_MENU_DATA if rm.role_id in user_roles]
        permissions = set()
        
        for menu_id in role_menus:
            menu = MENU_DATA_DICT.get(menu_id)
            if (menu and 
                menu.permission and 
                menu.permission.strip() and 
                menu.status == DisEnableStatusEnum.ENABLE):
                permissions.add(menu.permission)
        
        return permissions
    
    async def list_by_role_id(self, role_id: int) -> List[MenuEntity]:
        """
        根据角色ID查询菜单列表
        
        Args:
            role_id: 角色ID
            
        Returns:
            List[MenuEntity]: 菜单列表
        """
        # 如果有数据库会话，从数据库查询
        if self.db is not None:
            # TODO: 实现数据库查询逻辑
            # SELECT m.* FROM sys_menu m 
            # JOIN sys_role_menu rm ON m.id = rm.menu_id 
            # WHERE rm.role_id = ? AND m.status = 'ENABLE'
            # ORDER BY m.sort ASC
            pass
        
        # 使用默认测试数据
        # 检查是否为超级管理员角色
        super_admin_role = ROLE_DATA_DICT.get(1)  # ID=1的超级管理员角色
        if super_admin_role and role_id == 1:
            # 超级管理员拥有所有启用的菜单
            return [
                menu for menu in MENU_DATA_DICT.values() 
                if menu.status == DisEnableStatusEnum.ENABLE
            ]
        
        # 普通角色根据关联关系获取菜单
        role_menu_ids = [rm.menu_id for rm in ROLE_MENU_DATA if rm.role_id == role_id]
        menus = []
        
        for menu_id in role_menu_ids:
            menu = MENU_DATA_DICT.get(menu_id)
            if menu and menu.status == DisEnableStatusEnum.ENABLE:
                menus.append(menu)
        
        # 按排序字段排序
        return sorted(menus, key=lambda x: (x.sort, x.id))
    
    async def list_by_user_id(self, user_id: int) -> List[MenuEntity]:
        """
        根据用户ID查询菜单列表（通过用户的角色）
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[MenuEntity]: 菜单列表
        """
        # 获取用户的角色列表
        user_roles = [ur.role_id for ur in USER_ROLE_DATA if ur.user_id == user_id]
        if not user_roles:
            return []
        
        # 合并所有角色的菜单（去重）
        all_menus = set()
        for role_id in user_roles:
            role_menus = await self.list_by_role_id(role_id)
            all_menus.update(role_menus)
        
        # 转为列表并排序
        menu_list = list(all_menus)
        return sorted(menu_list, key=lambda x: (x.sort, x.id))
    
    async def build_menu_tree(self, menus: List[MenuEntity]) -> List[Dict[str, Any]]:
        """
        构建菜单树结构
        
        Args:
            menus: 菜单列表
            
        Returns:
            List[Dict[str, Any]]: 菜单树
        """
        if not menus:
            return []
        
        # 按父子关系构建树
        menu_dict = {menu.id: menu for menu in menus}
        tree = []
        
        def build_children(parent_id: int) -> List[Dict[str, Any]]:
            children = []
            for menu in menus:
                if menu.parent_id == parent_id:
                    menu_node = menu.to_route_config()
                    # 递归构建子菜单
                    child_nodes = build_children(menu.id)
                    if child_nodes:
                        menu_node['children'] = child_nodes
                    children.append(menu_node)
            
            # 按排序字段排序
            return sorted(children, key=lambda x: menus[next(i for i, m in enumerate(menus) if m.id == x['id'])].sort)
        
        # 构建根节点（parent_id = 0）
        return build_children(0)
    
    async def filter_visible_menus(self, menus: List[MenuEntity], exclude_buttons: bool = True) -> List[MenuEntity]:
        """
        过滤可见菜单
        
        Args:
            menus: 菜单列表
            exclude_buttons: 是否排除按钮类型菜单，默认True
            
        Returns:
            List[MenuEntity]: 过滤后的菜单列表
        """
        filtered_menus = []
        
        for menu in menus:
            # 检查菜单是否可见
            if not menu.is_visible():
                continue
            
            # 排除按钮类型（用于路由构建）
            if exclude_buttons and menu.is_button():
                continue
            
            filtered_menus.append(menu)
        
        return filtered_menus
    
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
        
        # 过滤可见菜单（排除按钮）
        visible_menus = await self.filter_visible_menus(user_menus, exclude_buttons=True)
        
        # 构建树结构
        return await self.build_menu_tree(visible_menus)


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