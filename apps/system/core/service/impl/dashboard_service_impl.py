# -*- coding: utf-8 -*-
"""
仪表盘服务实现

@author: continew-admin
@since: 2023/1/22 21:48
"""

from typing import List

from ..dashboard_service import DashboardService
from .notice_service_impl import NoticeServiceImpl
from apps.system.core.model.resp.dashboard_notice_resp import DashboardNoticeResp


class DashboardServiceImpl(DashboardService):
    """仪表盘服务实现"""
    
    def __init__(self):
        self.notice_service = NoticeServiceImpl()
    
    async def list_notice(self) -> List[DashboardNoticeResp]:
        """
        查询公告列表

        一比一复刻参考项目 DashboardServiceImpl.listNotice()

        Returns:
            List[DashboardNoticeResp]: 公告列表
        """
        from apps.common.context.user_context_holder import UserContextHolder

        user_id = UserContextHolder.get_user_id()
        return await self.notice_service.list_dashboard(user_id)