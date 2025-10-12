# -*- coding: utf-8 -*-
"""
公告状态枚举

一比一复刻参考项目 NoticeStatusEnum.java
@author: FlowMaster
@since: 2025/9/26
"""

from enum import Enum


class NoticeStatusEnum(int, Enum):
    """
    公告状态枚举

    一比一复刻参考项目 NoticeStatusEnum.java
    public enum NoticeStatusEnum implements BaseEnum<Integer> {
        DRAFT(1, "草稿"),
        PENDING(2, "待发布"),
        PUBLISHED(3, "已发布")
    }
    """

    # 草稿
    DRAFT = 1

    # 待发布
    PENDING = 2

    # 已发布
    PUBLISHED = 3

    @property
    def value_code(self) -> int:
        """获取数值编码（用于BaseEnum识别）"""
        return self.value

    @property
    def description(self) -> str:
        """获取描述（一比一复刻 getDescription()）"""
        mapping = {
            self.DRAFT: "草稿",
            self.PENDING: "待发布",
            self.PUBLISHED: "已发布",
        }
        return mapping[self]

    @property
    def color(self) -> str:
        """获取颜色（一比一复刻 getColor()）"""
        mapping = {
            self.DRAFT: "warning",
            self.PENDING: "primary",
            self.PUBLISHED: "success",
        }
        return mapping[self]

    @classmethod
    def from_value(cls, value: int) -> 'NoticeStatusEnum':
        """根据数值获取枚举值"""
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"Invalid NoticeStatusEnum value: {value}")