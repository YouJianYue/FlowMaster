# -*- coding: utf-8 -*-

"""
启用/禁用状态枚举
"""

from .base_enum import BaseEnum


class DisEnableStatusEnum(BaseEnum):
    """启用/禁用状态枚举"""
    
    ENABLE = 1   # 启用
    DISABLE = 2  # 禁用
    
    @property
    def description(self) -> str:
        """获取枚举描述"""
        descriptions = {
            1: "启用",
            2: "禁用"
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