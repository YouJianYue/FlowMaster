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

        Returns:
            List[DashboardNoticeResp]: 公告列表
        """
        # TODO: 实现实际的数据库查询逻辑
        # 暂时返回空列表，避免频繁访问
        return []