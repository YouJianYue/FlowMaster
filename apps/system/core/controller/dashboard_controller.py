# -*- coding: utf-8 -*-
"""
仪表盘 API

@author: continew-admin
@since: 2023/1/22 21:48
"""

from fastapi import APIRouter
from typing import List

from apps.system.core.service.impl.dashboard_service_impl import DashboardServiceImpl
from apps.system.core.model.resp.dashboard_notice_resp import DashboardNoticeResp


router = APIRouter(prefix="/dashboard", tags=["仪表盘 API"])

# 服务实例
dashboard_service = DashboardServiceImpl()


@router.get("/notice", summary="查询公告列表", description="查询公告列表")
async def list_notice() -> List[DashboardNoticeResp]:
    """查询公告列表"""
    return await dashboard_service.list_notice()