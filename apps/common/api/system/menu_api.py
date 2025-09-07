# -*- coding: utf-8 -*-

"""
菜单业务API接口
"""

from abc import ABC, abstractmethod
from typing import List


class MenuApi(ABC):
    """菜单业务API接口"""
    
    @abstractmethod
    async def list_by_role_codes(self, role_codes: List[str]) -> List[dict]:
        """
        根据角色编码列表查询菜单
        
        Args:
            role_codes: 角色编码列表
            
        Returns:
            菜单列表
        """
        pass