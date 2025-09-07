# -*- coding: utf-8 -*-

"""
角色业务API接口

"""

from abc import ABC, abstractmethod
from typing import Optional


class RoleApi(ABC):
    """角色业务API接口"""
    
    @abstractmethod
    async def get_id_by_code(self, code: str) -> Optional[int]:
        """
        根据编码查询ID
        
        Args:
            code: 角色编码
            
        Returns:
            角色ID
        """
        pass
    
    @abstractmethod
    async def update_user_context(self, role_id: int) -> None:
        """
        更新用户上下文
        
        Args:
            role_id: 角色ID
        """
        pass