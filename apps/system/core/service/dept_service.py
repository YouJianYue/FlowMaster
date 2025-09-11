# -*- coding: utf-8 -*-
"""
部门服务接口

@author: continew-admin
@since: 2025/9/11 10:00
"""

from abc import ABC, abstractmethod
from typing import List

from apps.system.core.model.resp.dept_dict_tree_resp import DeptDictTreeResp


class DeptService(ABC):
    """部门服务接口"""
    
    @abstractmethod
    async def get_dict_tree(self) -> List[DeptDictTreeResp]:
        """
        获取部门字典树
        
        Returns:
            List[DeptDictTreeResp]: 部门字典树列表
        """
        pass