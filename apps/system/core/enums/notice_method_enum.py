# -*- coding: utf-8 -*-
"""
公告通知方式枚举

@author: continew-admin
@since: 2025/5/8 21:18
"""

from enum import IntEnum


class NoticeMethodEnum(IntEnum):
    """公告通知方式枚举"""
    
    # 系统消息
    SYSTEM_MESSAGE = 1
    # 登录弹窗
    POPUP = 2
    
    @property
    def description(self):
        """获取描述"""
        descriptions = {
            NoticeMethodEnum.SYSTEM_MESSAGE: "系统消息",
            NoticeMethodEnum.POPUP: "登录弹窗"
        }
        return descriptions.get(self, "未知")