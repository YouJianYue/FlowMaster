# -*- coding: utf-8 -*-
"""
通知服务实现

@author: continew-admin
@since: 2025/5/8 21:18
"""

from typing import Optional, List
from datetime import datetime

from ..notice_service import NoticeService
from apps.system.core.enums.notice_method_enum import NoticeMethodEnum
from apps.system.core.model.resp.notice_detail_resp import NoticeDetailResp


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
    
    async def get_by_id(self, notice_id: int) -> Optional[NoticeDetailResp]:
        """
        根据ID获取公告详情
        
        Args:
            notice_id: 公告ID
            
        Returns:
            Optional[NoticeDetailResp]: 公告详情，如果不存在则返回None
        """
        # TODO: 实现实际的数据库查询逻辑
        # 目前返回模拟数据
        
        # 模拟公告详情数据
        notice_details = {
            1: NoticeDetailResp(
                id=1,
                title="系统维护通知",
                content="为了提升系统性能和用户体验，我们计划于2024年9月11日晚上22:00-24:00进行系统维护升级。维护期间，系统可能出现短暂无法访问的情况，给您带来的不便敬请谅解。",
                type="1",
                is_top=True,
                status="1",
                publish_time=datetime(2024, 9, 10, 14, 30, 0),
                create_time=datetime(2024, 9, 10, 14, 0, 0),
                create_user="admin"
            ),
            2: NoticeDetailResp(
                id=2,
                title="新功能发布公告", 
                content="很高兴向大家宣布，我们的系统新增了多项实用功能：1. 数据导出功能 2. 批量操作功能 3. 高级搜索功能。欢迎大家使用并反馈意见。",
                type="2",
                is_top=False,
                status="1",
                publish_time=datetime(2024, 9, 8, 10, 0, 0),
                create_time=datetime(2024, 9, 8, 9, 30, 0),
                create_user="admin"
            ),
            3: NoticeDetailResp(
                id=3,
                title="安全提醒",
                content="请各位用户注意保护账号安全：1. 定期修改密码 2. 不要在公共场所登录 3. 及时退出系统。如发现异常情况，请及时联系管理员。",
                type="3",
                is_top=False,
                status="1",
                publish_time=datetime(2024, 9, 5, 16, 0, 0),
                create_time=datetime(2024, 9, 5, 15, 45, 0),
                create_user="admin"
            )
        }
        
        return notice_details.get(notice_id)