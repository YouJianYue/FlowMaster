# -*- coding: utf-8 -*-

"""
权限查询服务接口
根据用户ID查询用户权限，这是解决菜单操作列显示问题的核心
"""

from abc import ABC, abstractmethod
from typing import List, Set, Optional


class PermissionService(ABC):
    """权限查询服务接口"""
    
    @abstractmethod
    async def get_user_permissions(self, user_id: int) -> Set[str]:
        """
        根据用户ID获取用户权限码集合
        
        Args:
            user_id: 用户ID
            
        Returns:
            Set[str]: 权限码集合
        """
        pass
    
    @abstractmethod
    async def get_user_roles(self, user_id: int) -> List[str]:
        """
        根据用户ID获取用户角色编码列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[str]: 角色编码列表
        """
        pass
    
    @abstractmethod
    async def has_permission(self, user_id: int, permission: str) -> bool:
        """
        检查用户是否拥有指定权限
        
        Args:
            user_id: 用户ID
            permission: 权限码
            
        Returns:
            bool: 是否拥有权限
        """
        pass
    
    @abstractmethod
    async def has_any_permission(self, user_id: int, permissions: List[str]) -> bool:
        """
        检查用户是否拥有任意一个权限
        
        Args:
            user_id: 用户ID
            permissions: 权限码列表
            
        Returns:
            bool: 是否拥有任意权限
        """
        pass