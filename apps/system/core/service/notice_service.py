# -*- coding: utf-8 -*-
"""
通知服务接口

@author: continew-admin
@since: 2025/5/8 21:18
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from apps.system.core.enums.notice_method_enum import NoticeMethodEnum


class NoticeService(ABC):
    """通知服务接口"""
    
    @abstractmethod
    async def list_unread_ids_by_user_id(self, method: Optional[NoticeMethodEnum], user_id: int) -> List[int]:
        """
        查询用户未读通知ID列表
        
        Args:
            method: 通知方式
            user_id: 用户ID
            
        Returns:
            List[int]: 未读通知ID列表
        """
        pass