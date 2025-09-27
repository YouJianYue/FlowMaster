# -*- coding: utf-8 -*-
"""
公告状态枚举

一比一复刻参考项目 NoticeStatusEnum.java
@author: FlowMaster
@since: 2025/9/26
"""

from enum import Enum
from typing import Dict, Any


class NoticeStatusEnum(Enum):
    """
    公告状态枚举

    一比一复刻参考项目 NoticeStatusEnum.java
    """

    # 草稿
    DRAFT = (1, "草稿", "warning")

    # 待发布
    PENDING = (2, "待发布", "primary")

    # 已发布
    PUBLISHED = (3, "已发布", "success")

    def __init__(self, value: int, description: str, color: str):
        self.enum_value = value
        self.description = description
        self.color = color

    @property
    def value(self):
        return self.enum_value

    @classmethod
    def from_value(cls, value: int) -> 'NoticeStatusEnum':
        """根据值获取枚举实例"""
        for enum_item in cls:
            if enum_item.enum_value == value:
                return enum_item
        raise ValueError(f"No NoticeStatusEnum with value: {value}")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "value": self.enum_value,
            "description": self.description,
            "color": self.color
        }

    @classmethod
    def get_all_dict(cls) -> list[Dict[str, Any]]:
        """获取所有枚举的字典格式"""
        return [item.to_dict() for item in cls]