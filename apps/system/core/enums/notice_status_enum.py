# -*- coding: utf-8 -*-
"""
公告状态枚举

一比一复刻参考项目 NoticeStatusEnum.java
@author: FlowMaster
@since: 2025/9/26
"""

from enum import Enum


class NoticeStatusEnum(str, Enum):
    """
    公告状态枚举

    一比一复刻参考项目 NoticeStatusEnum.java
    """

    # 草稿
    DRAFT = "DRAFT"

    # 待发布
    PENDING = "PENDING"

    # 已发布
    PUBLISHED = "PUBLISHED"

    @property
    def value_code(self) -> int:
        """获取数值编码（一比一复刻 getValue()）"""
        mapping = {
            self.DRAFT: 1,
            self.PENDING: 2,
            self.PUBLISHED: 3,
        }
        return mapping[self]

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
    def from_value_code(cls, value_code: int) -> 'NoticeStatusEnum':
        """根据数值编码获取枚举值"""
        mapping = {
            1: cls.DRAFT,
            2: cls.PENDING,
            3: cls.PUBLISHED,
        }
        return mapping.get(value_code)