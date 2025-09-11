# -*- coding: utf-8 -*-
"""
用户服务接口

@author: continew-admin
@since: 2025/9/11 11:00
"""

from abc import ABC, abstractmethod
from typing import Optional, Union

from apps.system.core.model.resp.user_resp import UserResp
from apps.common.model.page_resp import PageResp


class UserService(ABC):
    """用户服务接口"""
    
    @abstractmethod
    async def get_user_page(
        self, 
        dept_id: Optional[Union[int, str]] = None,
        page: int = 1,
        size: int = 10,
        sort: Optional[str] = None
    ) -> PageResp[UserResp]:
        """
        分页查询用户列表
        
        Args:
            dept_id: 部门ID
            page: 页码
            size: 每页大小
            sort: 排序字段
            
        Returns:
            PageResp[UserResp]: 分页用户数据
        """
        pass