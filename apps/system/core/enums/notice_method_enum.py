# -*- coding: utf-8 -*-
"""
公告通知方式枚举

一比一复刻参考项目 NoticeMethodEnum.java
@author: FlowMaster
@since: 2025/9/26
"""

from enum import Enum


class NoticeMethodEnum(int, Enum):
    """
    公告通知方式枚举

    一比一复刻参考项目 NoticeMethodEnum.java
    public enum NoticeMethodEnum implements BaseEnum<Integer> {
        SYSTEM_MESSAGE(1, "系统消息"),
        POPUP(2, "登录弹窗")
    }
    """

    # 系统消息
    SYSTEM_MESSAGE = 1

    # 登录弹窗
    POPUP = 2

    @property
    def value_code(self) -> int:
        """获取数值编码（用于BaseEnum识别）"""
        return self.value

    @property
    def description(self) -> str:
        """获取描述（一比一复刻 getDescription()）"""
        mapping = {
            self.SYSTEM_MESSAGE: "系统消息",
            self.POPUP: "登录弹窗",
        }
        return mapping[self]

    @classmethod
    def from_value(cls, value: int) -> 'NoticeMethodEnum':
        """根据数值获取枚举值"""
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"Invalid NoticeMethodEnum value: {value}")