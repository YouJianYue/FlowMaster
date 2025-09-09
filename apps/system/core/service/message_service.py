# -*- coding: utf-8 -*-
"""
消息服务接口

@author: continew-admin
@since: 2023/11/2 23:00
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from apps.system.core.model.resp.message_unread_resp import MessageUnreadResp


class MessageService(ABC):
    """消息服务接口"""
    
    @abstractmethod
    async def count_unread_by_user_id(self, user_id: int, is_detail: Optional[bool] = False) -> MessageUnreadResp:
        """
        查询用户未读消息数量
        
        Args:
            user_id: 用户ID
            is_detail: 是否查询详情
            
        Returns:
            MessageUnreadResp: 未读消息响应
        """
        pass