# -*- coding: utf-8 -*-
"""
消息服务实现

@author: continew-admin
@since: 2023/11/2 23:00
"""

from typing import Optional, List

from ..message_service import MessageService
from apps.system.core.model.resp.message_unread_resp import MessageUnreadResp
from apps.system.core.model.resp.message_type_unread_resp import MessageTypeUnreadResp
from apps.system.core.enums.message_type_enum import MessageTypeEnum


class MessageServiceImpl(MessageService):
    """消息服务实现"""
    
    async def count_unread_by_user_id(self, user_id: int, is_detail: Optional[bool] = False) -> MessageUnreadResp:
        """
        查询用户未读消息数量
        
        Args:
            user_id: 用户ID
            is_detail: 是否查询详情
            
        Returns:
            MessageUnreadResp: 未读消息响应
        """
        # TODO: 实现实际的数据库查询逻辑
        # 目前返回模拟数据
        result = MessageUnreadResp()
        
        if is_detail:
            # 模拟详细数据
            detail_list = []
            for message_type in MessageTypeEnum:
                resp = MessageTypeUnreadResp()
                resp.type = message_type
                resp.count = 5  # 模拟数据
                detail_list.append(resp)
            
            result.details = detail_list
            result.total = sum(item.count for item in detail_list if item.count)
        else:
            # 只返回总数
            result.total = 10  # 模拟数据
            
        return result