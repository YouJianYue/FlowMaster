# -*- coding: utf-8 -*-
"""
公告通知范围枚举

一比一复刻参考项目 NoticeScopeEnum.java
@author: FlowMaster
@since: 2025/9/26
"""

from enum import Enum


class NoticeScopeEnum(int, Enum):
    """
    公告通知范围枚举

    一比一复刻参考项目 NoticeScopeEnum.java
    public enum NoticeScopeEnum implements BaseEnum<Integer> {
        ALL(1, "所有人"),
        USER(2, "指定用户")
    }
    """

    # 所有人
    ALL = 1

    # 指定用户
    USER = 2

    @property
    def value_code(self) -> int:
        """获取数值编码（用于BaseEnum识别）"""
        return self.value

    @property
    def description(self) -> str:
        """获取描述（一比一复刻 getDescription()）"""
        mapping = {
            self.ALL: "所有人",
            self.USER: "指定用户",
        }
        return mapping[self]

    @classmethod
    def from_value(cls, value: int) -> 'NoticeScopeEnum':
        """根据数值获取枚举值"""
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"Invalid NoticeScopeEnum value: {value}")