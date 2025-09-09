# -*- coding: utf-8 -*-
"""
仪表盘服务接口

@author: continew-admin
@since: 2023/1/22 21:48
"""

from abc import ABC, abstractmethod
from typing import List

from apps.system.core.model.resp.dashboard_notice_resp import DashboardNoticeResp


class DashboardService(ABC):
    """仪表盘服务接口"""
    
    @abstractmethod
    async def list_notice(self) -> List[DashboardNoticeResp]:
        """
        查询公告列表
        
        Returns:
            List[DashboardNoticeResp]: 公告列表
        """
        pass