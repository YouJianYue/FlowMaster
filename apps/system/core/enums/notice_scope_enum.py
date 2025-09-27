# -*- coding: utf-8 -*-
"""
公告通知范围枚举

一比一复刻参考项目 NoticeScopeEnum.java
@author: FlowMaster
@since: 2025/9/26
"""

from enum import Enum
from typing import Dict, Any


class NoticeScopeEnum(Enum):
    """
    公告通知范围枚举

    一比一复刻参考项目 NoticeScopeEnum.java
    """

    # 所有人
    ALL = (1, "所有人")

    # 指定用户
    USER = (2, "指定用户")

    def __init__(self, value: int, description: str):
        self.enum_value = value
        self.description = description

    @property
    def value(self):
        return self.enum_value

    @classmethod
    def from_value(cls, value: int) -> 'NoticeScopeEnum':
        """根据值获取枚举实例"""
        for enum_item in cls:
            if enum_item.enum_value == value:
                return enum_item
        raise ValueError(f"No NoticeScopeEnum with value: {value}")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "value": self.enum_value,
            "description": self.description
        }

    @classmethod
    def get_all_dict(cls) -> list[Dict[str, Any]]:
        """获取所有枚举的字典格式"""
        return [item.to_dict() for item in cls]