# -*- coding: utf-8 -*-
"""
公告日志服务接口

一比一复刻参考项目 NoticeLogService.java
@author: FlowMaster
@since: 2025/10/12
"""

from typing import List
from abc import ABC, abstractmethod


class NoticeLogService(ABC):
    """
    公告日志服务接口

    一比一复刻参考项目 NoticeLogService
    """

    @abstractmethod
    async def add(self, user_ids: List[int], notice_id: int) -> bool:
        """
        添加公告阅读记录

        一比一复刻参考项目 NoticeLogService.add()

        Args:
            user_ids: 用户ID列表
            notice_id: 公告ID

        Returns:
            bool: 是否有新增记录
        """
        pass

    @abstractmethod
    async def delete_by_notice_ids(self, notice_ids: List[int]) -> None:
        """
        根据公告ID删除阅读记录

        一比一复刻参考项目 NoticeLogService.deleteByNoticeIds()

        Args:
            notice_ids: 公告ID列表
        """
        pass

    @abstractmethod
    async def list_user_id_by_notice_id(self, notice_id: int) -> List[int]:
        """
        查询公告的阅读用户ID列表

        一比一复刻参考项目 NoticeLogService.listUserIdByNoticeId()

        Args:
            notice_id: 公告ID

        Returns:
            List[int]: 用户ID列表
        """
        pass
