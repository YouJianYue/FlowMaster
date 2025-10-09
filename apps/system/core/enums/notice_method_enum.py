# -*- coding: utf-8 -*-
"""
公告通知方式枚举

一比一复刻参考项目 NoticeMethodEnum.java
@author: FlowMaster
@since: 2025/9/26
"""

from enum import Enum


class NoticeMethodEnum(str, Enum):
    """
    公告通知方式枚举

    一比一复刻参考项目 NoticeMethodEnum.java
    """

    # 系统消息
    SYSTEM_MESSAGE = "SYSTEM_MESSAGE"

    # 登录弹窗
    POPUP = "POPUP"

    @property
    def value_code(self) -> int:
        """获取数值编码（一比一复刻 getValue()）"""
        mapping = {
            self.SYSTEM_MESSAGE: 1,
            self.POPUP: 2,
        }
        return mapping[self]

    @property
    def description(self) -> str:
        """获取描述（一比一复刻 getDescription()）"""
        mapping = {
            self.SYSTEM_MESSAGE: "系统消息",
            self.POPUP: "登录弹窗",
        }
        return mapping[self]

    @classmethod
    def from_value_code(cls, value_code: int) -> 'NoticeMethodEnum':
        """根据数值编码获取枚举值"""
        mapping = {
            1: cls.SYSTEM_MESSAGE,
            2: cls.POPUP,
        }
        return mapping.get(value_code)