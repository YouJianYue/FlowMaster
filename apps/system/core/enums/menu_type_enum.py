# -*- coding: utf-8 -*-

"""
菜单类型枚举
"""

from enum import IntEnum


class MenuTypeEnum(IntEnum):
    """菜单类型枚举"""
    
    DIRECTORY = 1  # 目录
    MENU = 2       # 菜单
    BUTTON = 3     # 按钮
    
    @classmethod
    def get_desc(cls, value: int) -> str:
        """获取菜单类型描述"""
        desc_map = {
            cls.DIRECTORY: "目录",
            cls.MENU: "菜单", 
            cls.BUTTON: "按钮"
        }
        return desc_map.get(value, "未知")