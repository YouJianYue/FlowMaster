# -*- coding: utf-8 -*-
"""
公告通知范围枚举

一比一复刻参考项目 NoticeScopeEnum.java
@author: FlowMaster
@since: 2025/9/26
"""

from enum import Enum


class NoticeScopeEnum(str, Enum):
    """
    公告通知范围枚举

    一比一复刻参考项目 NoticeScopeEnum.java
    """

    # 所有人
    ALL = "ALL"

    # 指定用户
    USER = "USER"

    @property
    def value_code(self) -> int:
        """获取数值编码（一比一复刻 getValue()）"""
        mapping = {
            self.ALL: 1,
            self.USER: 2,
        }
        return mapping[self]

    @property
    def description(self) -> str:
        """获取描述（一比一复刻 getDescription()）"""
        mapping = {
            self.ALL: "所有人",
            self.USER: "指定用户",
        }
        return mapping[self]

    @classmethod
    def from_value_code(cls, value_code: int) -> 'NoticeScopeEnum':
        """根据数值编码获取枚举值"""
        mapping = {
            1: cls.ALL,
            2: cls.USER,
        }
        return mapping.get(value_code)