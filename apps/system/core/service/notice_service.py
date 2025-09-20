# -*- coding: utf-8 -*-
"""
通知服务接口
@since: 2025/5/8 21:18
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from apps.system.core.enums.notice_method_enum import NoticeMethodEnum
from apps.system.core.model.resp.notice_detail_resp import NoticeDetailResp


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
    
    @abstractmethod
    async def get_by_id(self, notice_id: int) -> Optional[NoticeDetailResp]:
        """
        根据ID获取公告详情
        
        Args:
            notice_id: 公告ID
            
        Returns:
            Optional[NoticeDetailResp]: 公告详情，如果不存在则返回None
        """
        pass