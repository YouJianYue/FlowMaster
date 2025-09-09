# -*- coding: utf-8 -*-
"""
通知服务实现

@author: continew-admin
@since: 2025/5/8 21:18
"""

from typing import Optional, List

from ..notice_service import NoticeService
from apps.system.core.enums.notice_method_enum import NoticeMethodEnum


class NoticeServiceImpl(NoticeService):
    """通知服务实现"""
    
    async def list_unread_ids_by_user_id(self, method: Optional[NoticeMethodEnum], user_id: int) -> List[int]:
        """
        查询用户未读通知ID列表
        
        Args:
            method: 通知方式
            user_id: 用户ID
            
        Returns:
            List[int]: 未读通知ID列表
        """
        # TODO: 实现实际的数据库查询逻辑
        # 目前返回模拟数据
        if method == NoticeMethodEnum.POPUP:
            # POPUP方式的未读通知
            return [1, 2, 3]  # 模拟数据
        else:
            # 其他方式的未读通知
            return [1, 2]  # 模拟数据