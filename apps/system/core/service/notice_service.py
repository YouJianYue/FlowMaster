# -*- coding: utf-8 -*-
"""
通知服务接口
一比一复刻参考项目 NoticeService.java

@author: FlowMaster
@since: 2025/5/8 21:18
"""

from abc import abstractmethod
from typing import Optional, List

from apps.common.base.service.base_service import BaseService
from apps.system.core.enums.notice_method_enum import NoticeMethodEnum
from apps.system.core.model.entity.notice_entity import NoticeEntity
from apps.system.core.model.query.notice_query import NoticeQuery
from apps.system.core.model.req.notice_req import NoticeReq
from apps.system.core.model.resp.notice_resp import NoticeResp, NoticeDetailResp


class NoticeService(BaseService[NoticeResp, NoticeDetailResp, NoticeQuery, NoticeReq]):
    """
    通知服务接口
    一比一复刻参考项目 NoticeService
    """

    @abstractmethod
    async def publish(self, notice: NoticeEntity) -> None:
        """
        发布公告
        一比一复刻参考项目 NoticeService.publish()

        Args:
            notice: 公告信息
        """
        pass

    @abstractmethod
    async def list_unread_ids_by_user_id(self, method: Optional[NoticeMethodEnum], user_id: int) -> List[int]:
        """
        查询用户未读通知ID列表
        一比一复刻参考项目 NoticeService.listUnreadIdsByUserId()

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

    @abstractmethod
    async def read_notice(self, notice_id: int, user_id: int) -> None:
        """
        标记公告为已读

        一比一复刻参考项目 NoticeService.readNotice()

        Args:
            notice_id: 公告ID
            user_id: 用户ID
        """
        pass


def get_notice_service() -> NoticeService:
    """获取通知服务实例"""
    from apps.system.core.service.impl.notice_service_impl import NoticeServiceImpl
    return NoticeServiceImpl()