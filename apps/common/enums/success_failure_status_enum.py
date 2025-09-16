# -*- coding: utf-8 -*-

"""
成功/失败状态枚举
"""

from .base_enum import BaseEnum


class SuccessFailureStatusEnum(BaseEnum):
    """成功/失败状态枚举"""
    
    SUCCESS = 1  # 成功
    FAILURE = 2  # 失败
    
    @property
    def description(self) -> str:
        """获取枚举描述"""
        descriptions = {
            1: "成功",
            2: "失败"
        }
        return descriptions.get(self.value, "未知")
    
    @property
    def color(self) -> str:
        """获取UI颜色"""
        colors = {
            1: "success",
            2: "error"
        }
        return colors.get(self.value, "default")